-- =============================================================================
-- MARKETPLACE UNIVERSIDAD SANTIAGO DE CALI (USC) - CONSTRUCCIÓN DE SOFTWARE II
-- ESQUEMA MODULAR PARA MICROSERVICIOS INDEPENDIENTES (DATABASE-PER-SERVICE)
-- =============================================================================
-- Cada equipo cuenta con su propia base de datos autónoma en Supabase.
-- Las relaciones inter-módulos se gestionan mediante UUIDs canónicos y llamadas REST.
-- =============================================================================

-- =============================================================================
-- NÚCLEO CENTRAL / AUTH & PERFILES (Tu Proyecto Supabase Principal)
-- Proyecto: https://xmrlazemifmepyahqsrz.supabase.co
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.usr_perfiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(50),
    direccion TEXT,
    ciudad VARCHAR(100) DEFAULT 'Cali',
    rol VARCHAR(30) NOT NULL CHECK (rol IN ('ADMIN', 'VENDEDOR', 'COMPRADOR')),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usr_perfiles_rol ON public.usr_perfiles(rol);
CREATE INDEX IF NOT EXISTS idx_usr_perfiles_email ON public.usr_perfiles(email);

-- Trigger de sincronización automática desde auth.users
CREATE OR REPLACE FUNCTION public.handle_nuevo_usuario()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.usr_perfiles (id, email, nombre, rol, telefono, direccion)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'nombre', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'rol', 'COMPRADOR'),
        COALESCE(NEW.raw_user_meta_data->>'telefono', ''),
        COALESCE(NEW.raw_user_meta_data->>'direccion', '')
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        nombre = EXCLUDED.nombre,
        rol = EXCLUDED.rol;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS tr_on_auth_user_created ON auth.users;
CREATE TRIGGER tr_on_auth_user_created
    AFTER INSERT OR UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_nuevo_usuario();

-- Sincronizar usuarios existentes
INSERT INTO public.usr_perfiles (id, email, nombre, rol)
SELECT id, email, COALESCE(raw_user_meta_data->>'nombre', split_part(email, '@', 1)), COALESCE(raw_user_meta_data->>'rol', 'COMPRADOR')
FROM auth.users
ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- ESQUEMA EQUIPO 3: NOTIFICACIONES (Microservicio Propio)
-- Totalmente desacoplado. usuario_id almacena el UUID del usuario del Login central.
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.notif_mensajes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (
        tipo IN (
            'ORDEN_CREADA', 'PAGO_APROBADO', 'PAGO_RECHAZADO',
            'ENVIO_EN_TRANSITO', 'ENVIO_ENTREGADO', 'STOCK_BAJO',
            'DEVOLUCION_SOLICITADA', 'REEMBOLSO_PROCESADO',
            'ESCROW_LIBERADO', 'INCIDENCIA_PQR', 'SISTEMA_INFO'
        )
    ),
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    referencia_id VARCHAR(100),
    referencia_tipo VARCHAR(50) DEFAULT 'ORDEN',
    leido BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    leido_en TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_notif_usuario ON public.notif_mensajes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_notif_leido ON public.notif_mensajes(leido);

-- =============================================================================
-- ESQUEMA EQUIPO 6: CONTABILIDAD, CONCILIACIÓN Y ESCROW (Microservicio Propio)
-- Totalmente desacoplado. vendedor_id, comprador_id y pedido_id almacenan UUIDs canónicos.
-- Reglas: Comisión del 5%, Escrow liberación 72h o conformidad del cliente
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.cont_cuentas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL UNIQUE,
    saldo_disponible NUMERIC(14, 2) NOT NULL DEFAULT 0.00 CHECK (saldo_disponible >= 0),
    saldo_en_custodia NUMERIC(14, 2) NOT NULL DEFAULT 0.00 CHECK (saldo_en_custodia >= 0),
    total_ventas_brutas NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    total_comisiones_pagadas NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.cont_escrow (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pedido_id UUID NOT NULL UNIQUE,
    vendedor_id UUID NOT NULL,
    comprador_id UUID NOT NULL,
    monto_bruto NUMERIC(14, 2) NOT NULL CHECK (monto_bruto >= 0),
    porcentaje_comision NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    comision_plataforma NUMERIC(14, 2) NOT NULL CHECK (comision_plataforma >= 0),
    monto_neto_vendedor NUMERIC(14, 2) NOT NULL CHECK (monto_neto_vendedor >= 0),
    estado_escrow VARCHAR(30) NOT NULL DEFAULT 'RETENIDO' CHECK (
        estado_escrow IN ('RETENIDO', 'LIBERADO', 'BLOQUEADO_PQR', 'REEMBOLSADO')
    ),
    motivo_liberacion VARCHAR(40) CHECK (motivo_liberacion IN ('72_HORAS_EXPIRADAS', 'CONFORMIDAD_CLIENTE', 'MANUAL_ADMIN', NULL)),
    fecha_entrega TIMESTAMP WITH TIME ZONE,
    fecha_limite_liberacion TIMESTAMP WITH TIME ZONE,
    fecha_liberacion_real TIMESTAMP WITH TIME ZONE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cont_escrow_vendedor ON public.cont_escrow(vendedor_id);
CREATE INDEX IF NOT EXISTS idx_cont_escrow_estado ON public.cont_escrow(estado_escrow);

CREATE TABLE IF NOT EXISTS public.cont_movimientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cuenta_id UUID REFERENCES public.cont_cuentas(id) ON DELETE SET NULL,
    pedido_id UUID,
    tipo VARCHAR(40) NOT NULL CHECK (
        tipo IN (
            'VENTA_INGRESO_ESCROW',
            'COMISION_PLATAFORMA_5PCT',
            'LIBERACION_ESCROW_A_SALDO',
            'BLOQUEO_PQR',
            'REEMBOLSO_COMPRADOR',
            'RETIRO_VENDEDOR'
        )
    ),
    naturaleza VARCHAR(10) NOT NULL CHECK (naturaleza IN ('DEBITO', 'CREDITO')),
    monto NUMERIC(14, 2) NOT NULL CHECK (monto >= 0),
    saldo_anterior NUMERIC(14, 2) NOT NULL,
    saldo_nuevo NUMERIC(14, 2) NOT NULL,
    descripcion TEXT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- =============================================================================
-- POLÍTICAS RLS (Row Level Security)
-- =============================================================================
ALTER TABLE public.usr_perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notif_mensajes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cont_cuentas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cont_escrow ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cont_movimientos ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('usr_perfiles', 'notif_mensajes', 'cont_cuentas', 'cont_escrow', 'cont_movimientos')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', 'policy_all_' || t, t);
        EXECUTE format('CREATE POLICY %I ON public.%I FOR ALL USING (true) WITH CHECK (true)', 'policy_all_' || t, t);
    END LOOP;
END $$;
