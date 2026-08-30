--
-- PostgreSQL database dump
--

\restrict cMs6O96GyWgnOa90zUcKT3NKnlLkp44oeQdnQTPBIhX8qA8gWii3M09S4lgewYd

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.access_log (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    username character varying(64) NOT NULL,
    warehouse_id character varying(20),
    action character varying(50) NOT NULL,
    ip_address character varying(45)
);


ALTER TABLE public.access_log OWNER TO postgres;

--
-- Name: access_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.access_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_log_id_seq OWNER TO postgres;

--
-- Name: access_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.access_log_id_seq OWNED BY public.access_log.id;


--
-- Name: ai_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_recommendations (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(50),
    title character varying(100) NOT NULL,
    risk_level character varying(20),
    action_recommended character varying(100) NOT NULL,
    confidence_score integer,
    input_factors text,
    status character varying(20),
    decision_by character varying(64),
    decision_time timestamp without time zone,
    notes text,
    recommendation_type character varying(50),
    description text,
    priority character varying(20),
    score integer,
    confidence_or_reliability character varying(50),
    source_model character varying(50),
    source_entity_type character varying(50),
    source_entity_id character varying(50),
    recommended_action character varying(200),
    estimated_impact double precision,
    explanation text,
    supporting_metrics text,
    created_at timestamp without time zone NOT NULL,
    reviewed_at timestamp without time zone,
    reviewed_by character varying(64),
    review_notes text,
    expires_at timestamp without time zone,
    metadata text NOT NULL
);


ALTER TABLE public.ai_recommendations OWNER TO postgres;

--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ai_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_recommendations_id_seq OWNER TO postgres;

--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ai_recommendations_id_seq OWNED BY public.ai_recommendations.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: audit_ledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_ledger (
    id integer NOT NULL,
    "timestamp" timestamp without time zone,
    event_type character varying(50) NOT NULL,
    details text,
    prev_hash character varying(64) NOT NULL,
    hash character varying(64) NOT NULL
);


ALTER TABLE public.audit_ledger OWNER TO postgres;

--
-- Name: audit_ledger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_ledger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_ledger_id_seq OWNER TO postgres;

--
-- Name: audit_ledger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_ledger_id_seq OWNED BY public.audit_ledger.id;


--
-- Name: backup_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backup_records (
    id integer NOT NULL,
    backup_id character varying(64) NOT NULL,
    filename character varying(255) NOT NULL,
    created_at timestamp without time zone,
    size_bytes integer,
    sha256 character varying(64),
    status character varying(20) NOT NULL,
    storage_key character varying(255),
    error_message text,
    backup_type character varying(50),
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    storage_provider character varying(50),
    bucket character varying(255),
    checksum_algorithm character varying(20),
    verification_status character varying(50),
    verification_at timestamp without time zone,
    restore_test_status character varying(50),
    restore_test_at timestamp without time zone,
    retention_status character varying(50),
    initiated_by character varying(100),
    audit_ref character varying(255)
);


ALTER TABLE public.backup_records OWNER TO postgres;

--
-- Name: backup_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backup_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.backup_records_id_seq OWNER TO postgres;

--
-- Name: backup_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backup_records_id_seq OWNED BY public.backup_records.id;


--
-- Name: digital_twin_simulations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.digital_twin_simulations (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    simulation_status character varying(20) NOT NULL,
    simulation_time_seconds double precision NOT NULL,
    speed_multiplier double precision NOT NULL,
    seed integer NOT NULL,
    mode character varying(20) NOT NULL,
    scenario_type character varying(30) NOT NULL,
    tick_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    started_at timestamp without time zone,
    paused_at timestamp without time zone,
    stopped_at timestamp without time zone,
    completed_at timestamp without time zone,
    error_message text,
    created_by character varying(64) NOT NULL
);


ALTER TABLE public.digital_twin_simulations OWNER TO postgres;

--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.digital_twin_simulations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.digital_twin_simulations_id_seq OWNER TO postgres;

--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.digital_twin_simulations_id_seq OWNED BY public.digital_twin_simulations.id;


--
-- Name: experiment_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment_runs (
    id integer NOT NULL,
    experiment_id integer NOT NULL,
    repetition_number integer NOT NULL,
    random_seed integer NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds double precision,
    error_message text,
    metrics json,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.experiment_runs OWNER TO postgres;

--
-- Name: experiment_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiment_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiment_runs_id_seq OWNER TO postgres;

--
-- Name: experiment_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiment_runs_id_seq OWNED BY public.experiment_runs.id;


--
-- Name: experiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiments (
    id integer NOT NULL,
    scenario_id integer NOT NULL,
    experiment_name character varying(150) NOT NULL,
    description text,
    status character varying(20) NOT NULL,
    algorithm_name character varying(50) NOT NULL,
    algorithm_version character varying(20) NOT NULL,
    configuration json NOT NULL,
    random_seed integer NOT NULL,
    repetitions integer NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds double precision,
    created_by character varying(64) NOT NULL,
    error_message text,
    metrics_summary json,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.experiments OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiments_id_seq OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiments_id_seq OWNED BY public.experiments.id;


--
-- Name: health_thresholds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_thresholds (
    id integer NOT NULL,
    key character varying(64) NOT NULL,
    value double precision NOT NULL,
    description character varying(255),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.health_thresholds OWNER TO postgres;

--
-- Name: health_thresholds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.health_thresholds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.health_thresholds_id_seq OWNER TO postgres;

--
-- Name: health_thresholds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.health_thresholds_id_seq OWNED BY public.health_thresholds.id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    location_id character varying(50),
    on_hand integer NOT NULL,
    reserved integer NOT NULL,
    available integer NOT NULL,
    damaged integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.inventory OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_id_seq OWNER TO postgres;

--
-- Name: inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_id_seq OWNED BY public.inventory.id;


--
-- Name: inventory_reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory_reservations (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    location_id character varying(50),
    reserved_qty integer NOT NULL,
    released_qty integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.inventory_reservations OWNER TO postgres;

--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_reservations_id_seq OWNER TO postgres;

--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_reservations_id_seq OWNED BY public.inventory_reservations.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.items (
    id character varying(20) NOT NULL,
    name character varying(150) NOT NULL,
    category character varying(80),
    unit_cost double precision,
    lead_time_days integer,
    safety_stock integer,
    sku character varying(64),
    description text,
    unit character varying(20),
    weight_kg double precision,
    dimensions character varying(50),
    barcode character varying(64),
    is_active boolean,
    reorder_threshold integer,
    preferred_storage_type character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.items OWNER TO postgres;

--
-- Name: notification_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_preferences (
    id integer NOT NULL,
    user_id integer NOT NULL,
    category character varying(50) NOT NULL,
    in_app_enabled boolean NOT NULL,
    email_enabled boolean NOT NULL,
    min_severity character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.notification_preferences OWNER TO postgres;

--
-- Name: notification_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_preferences_id_seq OWNER TO postgres;

--
-- Name: notification_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_preferences_id_seq OWNED BY public.notification_preferences.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    warehouse_id character varying(20),
    event_type character varying(50) NOT NULL,
    notification_type character varying(50) NOT NULL,
    title character varying(150) NOT NULL,
    message text NOT NULL,
    severity character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    channel character varying(20) NOT NULL,
    source_entity_type character varying(50),
    source_entity_id character varying(50),
    created_at timestamp without time zone NOT NULL,
    read_at timestamp without time zone,
    delivered_at timestamp without time zone,
    failed_at timestamp without time zone,
    retry_count integer NOT NULL,
    expires_at timestamp without time zone,
    metadata text NOT NULL,
    idempotency_key character varying(255)
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: order_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_events (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    "timestamp" timestamp without time zone,
    status character varying(30) NOT NULL,
    event_type character varying(50) NOT NULL,
    operator character varying(64),
    notes text
);


ALTER TABLE public.order_events OWNER TO postgres;

--
-- Name: order_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_events_id_seq OWNER TO postgres;

--
-- Name: order_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_events_id_seq OWNED BY public.order_events.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    requested_qty integer NOT NULL,
    reserved_qty integer NOT NULL,
    picked_qty integer NOT NULL,
    packed_qty integer NOT NULL,
    shipped_qty integer NOT NULL,
    status character varying(20) NOT NULL
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id character varying(20) NOT NULL,
    customer_ref character varying(100) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    status character varying(30) NOT NULL,
    priority character varying(20) NOT NULL,
    total_items integer NOT NULL,
    notes text,
    created_by character varying(64)
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: otp_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otp_records (
    id integer NOT NULL,
    user_id integer NOT NULL,
    purpose character varying(50) NOT NULL,
    code_hash character varying(255) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    attempts integer NOT NULL,
    max_attempts integer NOT NULL,
    consumed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    request_ip character varying(45),
    context_data text
);


ALTER TABLE public.otp_records OWNER TO postgres;

--
-- Name: otp_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.otp_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.otp_records_id_seq OWNER TO postgres;

--
-- Name: otp_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.otp_records_id_seq OWNED BY public.otp_records.id;


--
-- Name: packing_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.packing_records (
    id integer NOT NULL,
    order_id character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    operator character varying(64),
    package_count integer NOT NULL,
    weight_kg double precision,
    notes text
);


ALTER TABLE public.packing_records OWNER TO postgres;

--
-- Name: packing_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.packing_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.packing_records_id_seq OWNER TO postgres;

--
-- Name: packing_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.packing_records_id_seq OWNED BY public.packing_records.id;


--
-- Name: recovery_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recovery_codes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    code_hash character varying(255) NOT NULL,
    used boolean NOT NULL,
    created_at timestamp without time zone,
    used_at timestamp without time zone
);


ALTER TABLE public.recovery_codes OWNER TO postgres;

--
-- Name: recovery_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recovery_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recovery_codes_id_seq OWNER TO postgres;

--
-- Name: recovery_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recovery_codes_id_seq OWNED BY public.recovery_codes.id;


--
-- Name: recovery_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recovery_credentials (
    id integer NOT NULL,
    user_id integer NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.recovery_credentials OWNER TO postgres;

--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recovery_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recovery_credentials_id_seq OWNER TO postgres;

--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recovery_credentials_id_seq OWNED BY public.recovery_credentials.id;


--
-- Name: robot_reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_reservations (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    tick integer NOT NULL
);


ALTER TABLE public.robot_reservations OWNER TO postgres;

--
-- Name: robot_reservations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_reservations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_reservations_id_seq OWNER TO postgres;

--
-- Name: robot_reservations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_reservations_id_seq OWNED BY public.robot_reservations.id;


--
-- Name: robot_routes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_routes (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    task_id integer,
    warehouse_id character varying(20) NOT NULL,
    start_x integer NOT NULL,
    start_y integer NOT NULL,
    goal_x integer NOT NULL,
    goal_y integer NOT NULL,
    algorithm character varying(30) NOT NULL,
    path_data text NOT NULL,
    distance double precision NOT NULL,
    cost double precision NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone
);


ALTER TABLE public.robot_routes OWNER TO postgres;

--
-- Name: robot_routes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_routes_id_seq OWNER TO postgres;

--
-- Name: robot_routes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_routes_id_seq OWNED BY public.robot_routes.id;


--
-- Name: robot_telemetry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robot_telemetry (
    id integer NOT NULL,
    robot_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    battery double precision NOT NULL,
    status character varying(30) NOT NULL,
    task_id integer,
    metadata text NOT NULL
);


ALTER TABLE public.robot_telemetry OWNER TO postgres;

--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robot_telemetry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robot_telemetry_id_seq OWNER TO postgres;

--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robot_telemetry_id_seq OWNED BY public.robot_telemetry.id;


--
-- Name: robots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.robots (
    id integer NOT NULL,
    robot_code character varying(30) NOT NULL,
    name character varying(100) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    status character varying(30) NOT NULL,
    battery_level double precision NOT NULL,
    current_location_id character varying(50),
    current_x double precision NOT NULL,
    current_y double precision NOT NULL,
    target_location_id character varying(50),
    target_x double precision NOT NULL,
    target_y double precision NOT NULL,
    assigned_task_id integer,
    total_tasks_completed integer NOT NULL,
    total_distance double precision NOT NULL,
    total_operating_time double precision NOT NULL,
    utilization_percent double precision NOT NULL,
    failure_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    last_heartbeat_at timestamp without time zone NOT NULL,
    robot_type character varying(30) NOT NULL,
    max_payload double precision NOT NULL,
    max_speed double precision NOT NULL,
    enabled boolean NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.robots OWNER TO postgres;

--
-- Name: robots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.robots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.robots_id_seq OWNER TO postgres;

--
-- Name: robots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.robots_id_seq OWNED BY public.robots.id;


--
-- Name: scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scenarios (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    warehouse_id character varying(20) NOT NULL,
    scenario_type character varying(30) NOT NULL,
    configuration json NOT NULL,
    random_seed integer NOT NULL,
    status character varying(20) NOT NULL,
    tags text NOT NULL,
    notes text,
    created_by character varying(64) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.scenarios OWNER TO postgres;

--
-- Name: scenarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scenarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scenarios_id_seq OWNER TO postgres;

--
-- Name: scenarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scenarios_id_seq OWNED BY public.scenarios.id;


--
-- Name: shipments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipments (
    id character varying(20) NOT NULL,
    order_id character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    tracking_reference character varying(100),
    carrier character varying(50),
    created_at timestamp without time zone,
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone
);


ALTER TABLE public.shipments OWNER TO postgres;

--
-- Name: shrinkage_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shrinkage_flags (
    id integer NOT NULL,
    date date NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    item_name character varying(150),
    deviation_score double precision,
    expected_quantity double precision,
    actual_quantity double precision,
    discrepancy_quantity double precision,
    estimated_exposure double precision,
    severity character varying(20),
    likely_cause character varying(80),
    explanation text
);


ALTER TABLE public.shrinkage_flags OWNER TO postgres;

--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shrinkage_flags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shrinkage_flags_id_seq OWNER TO postgres;

--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shrinkage_flags_id_seq OWNED BY public.shrinkage_flags.id;


--
-- Name: simulation_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_events (
    id integer NOT NULL,
    simulation_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    event_type character varying(50) NOT NULL,
    severity character varying(10) NOT NULL,
    sim_time_seconds double precision NOT NULL,
    real_timestamp timestamp without time zone NOT NULL,
    robot_id integer,
    task_id integer,
    location_id character varying(50),
    route_id integer,
    message text NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.simulation_events OWNER TO postgres;

--
-- Name: simulation_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simulation_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simulation_events_id_seq OWNER TO postgres;

--
-- Name: simulation_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simulation_events_id_seq OWNED BY public.simulation_events.id;


--
-- Name: simulation_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_snapshots (
    id integer NOT NULL,
    simulation_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    snapshot_version integer NOT NULL,
    taken_at timestamp without time zone NOT NULL,
    sim_time_seconds double precision NOT NULL,
    robot_states text NOT NULL,
    task_states text NOT NULL,
    obstacle_states text NOT NULL,
    sim_inventory_delta text NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.simulation_snapshots OWNER TO postgres;

--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simulation_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simulation_snapshots_id_seq OWNER TO postgres;

--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simulation_snapshots_id_seq OWNED BY public.simulation_snapshots.id;


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_movements (
    id integer NOT NULL,
    date date NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    item_id character varying(20) NOT NULL,
    stock_in integer,
    stock_out integer,
    closing_stock integer,
    is_anomaly boolean,
    anomaly_type character varying(30),
    entry_source character varying(20),
    entered_by character varying(64)
);


ALTER TABLE public.stock_movements OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_movements_id_seq OWNER TO postgres;

--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_movements_id_seq OWNED BY public.stock_movements.id;


--
-- Name: system_health_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_health_snapshots (
    id integer NOT NULL,
    service character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    latency_ms double precision,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.system_health_snapshots OWNER TO postgres;

--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_health_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_health_snapshots_id_seq OWNER TO postgres;

--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_health_snapshots_id_seq OWNED BY public.system_health_snapshots.id;


--
-- Name: system_incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_incidents (
    id integer NOT NULL,
    category character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    title character varying(100) NOT NULL,
    description text NOT NULL,
    source character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    fingerprint character varying(128),
    started_at timestamp without time zone NOT NULL,
    resolved_at timestamp without time zone,
    acknowledged_by character varying(64),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.system_incidents OWNER TO postgres;

--
-- Name: system_incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_incidents_id_seq OWNER TO postgres;

--
-- Name: system_incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_incidents_id_seq OWNED BY public.system_incidents.id;


--
-- Name: task_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_events (
    id integer NOT NULL,
    task_id integer NOT NULL,
    event_type character varying(50) NOT NULL,
    previous_status character varying(30),
    new_status character varying(30),
    user_id integer,
    created_at timestamp without time zone NOT NULL,
    reason text,
    metadata text NOT NULL
);


ALTER TABLE public.task_events OWNER TO postgres;

--
-- Name: task_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.task_events_id_seq OWNER TO postgres;

--
-- Name: task_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_events_id_seq OWNED BY public.task_events.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    task_number character varying(64) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    task_type character varying(30) NOT NULL,
    priority character varying(20) NOT NULL,
    priority_score integer NOT NULL,
    status character varying(30) NOT NULL,
    source_type character varying(30),
    source_id character varying(64),
    order_id character varying(20),
    order_item_id integer,
    product_id character varying(20) NOT NULL,
    source_location_id character varying(50),
    destination_location_id character varying(50),
    requested_quantity integer NOT NULL,
    completed_quantity integer NOT NULL,
    assigned_user_id integer,
    assigned_robot_id character varying(50),
    created_at timestamp without time zone,
    prioritized_at timestamp without time zone,
    assigned_at timestamp without time zone,
    started_at timestamp without time zone,
    paused_at timestamp without time zone,
    completed_at timestamp without time zone,
    failed_at timestamp without time zone,
    cancelled_at timestamp without time zone,
    due_at timestamp without time zone,
    retry_count integer NOT NULL,
    failure_reason text,
    notes text,
    metadata text NOT NULL,
    depends_on_task_id integer
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO postgres;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_token_hash character varying(64) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_seen_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    revoked_at timestamp without time zone,
    revoke_reason character varying(100),
    login_method character varying(30),
    ip_address character varying(45),
    login_location character varying(255),
    user_agent character varying(500)
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: user_warehouse_access; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_warehouse_access (
    id integer NOT NULL,
    user_id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_warehouse_access OWNER TO postgres;

--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_warehouse_access_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_warehouse_access_id_seq OWNER TO postgres;

--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_warehouse_access_id_seq OWNED BY public.user_warehouse_access.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(255),
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    full_name character varying(120),
    google_subject_id character varying(128),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active boolean NOT NULL,
    is_verified boolean NOT NULL,
    last_login_at timestamp without time zone,
    last_logout_at timestamp without time zone,
    last_login_ip character varying(45),
    login_location character varying(255),
    login_method character varying(30),
    failed_login_count integer NOT NULL,
    locked_until timestamp without time zone,
    email_verified_at timestamp without time zone,
    password_changed_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: warehouse_grid_cells; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_grid_cells (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    cell_type character varying(30) NOT NULL,
    traversable boolean NOT NULL,
    occupied boolean NOT NULL,
    restricted boolean NOT NULL,
    cost double precision NOT NULL,
    metadata text NOT NULL
);


ALTER TABLE public.warehouse_grid_cells OWNER TO postgres;

--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_grid_cells_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_grid_cells_id_seq OWNER TO postgres;

--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_grid_cells_id_seq OWNED BY public.warehouse_grid_cells.id;


--
-- Name: warehouse_locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_locations (
    id character varying(50) NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    zone character varying(20) NOT NULL,
    aisle character varying(20) NOT NULL,
    rack character varying(20) NOT NULL,
    shelf character varying(20) NOT NULL,
    x double precision,
    y double precision,
    capacity integer,
    current_utilization integer,
    location_type character varying(20),
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.warehouse_locations OWNER TO postgres;

--
-- Name: warehouse_obstacles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse_obstacles (
    id integer NOT NULL,
    warehouse_id character varying(20) NOT NULL,
    obstacle_type character varying(30) NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    active boolean NOT NULL,
    severity character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.warehouse_obstacles OWNER TO postgres;

--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_obstacles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warehouse_obstacles_id_seq OWNER TO postgres;

--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_obstacles_id_seq OWNED BY public.warehouse_obstacles.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouses (
    id character varying(20) NOT NULL,
    name character varying(120) NOT NULL,
    location character varying(120),
    latitude double precision,
    longitude double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.warehouses OWNER TO postgres;

--
-- Name: access_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_log ALTER COLUMN id SET DEFAULT nextval('public.access_log_id_seq'::regclass);


--
-- Name: ai_recommendations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_recommendations ALTER COLUMN id SET DEFAULT nextval('public.ai_recommendations_id_seq'::regclass);


--
-- Name: audit_ledger id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_ledger ALTER COLUMN id SET DEFAULT nextval('public.audit_ledger_id_seq'::regclass);


--
-- Name: backup_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_records ALTER COLUMN id SET DEFAULT nextval('public.backup_records_id_seq'::regclass);


--
-- Name: digital_twin_simulations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations ALTER COLUMN id SET DEFAULT nextval('public.digital_twin_simulations_id_seq'::regclass);


--
-- Name: experiment_runs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs ALTER COLUMN id SET DEFAULT nextval('public.experiment_runs_id_seq'::regclass);


--
-- Name: experiments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments ALTER COLUMN id SET DEFAULT nextval('public.experiments_id_seq'::regclass);


--
-- Name: health_thresholds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_thresholds ALTER COLUMN id SET DEFAULT nextval('public.health_thresholds_id_seq'::regclass);


--
-- Name: inventory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN id SET DEFAULT nextval('public.inventory_id_seq'::regclass);


--
-- Name: inventory_reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations ALTER COLUMN id SET DEFAULT nextval('public.inventory_reservations_id_seq'::regclass);


--
-- Name: notification_preferences id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences ALTER COLUMN id SET DEFAULT nextval('public.notification_preferences_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: order_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events ALTER COLUMN id SET DEFAULT nextval('public.order_events_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: otp_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records ALTER COLUMN id SET DEFAULT nextval('public.otp_records_id_seq'::regclass);


--
-- Name: packing_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records ALTER COLUMN id SET DEFAULT nextval('public.packing_records_id_seq'::regclass);


--
-- Name: recovery_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes ALTER COLUMN id SET DEFAULT nextval('public.recovery_codes_id_seq'::regclass);


--
-- Name: recovery_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials ALTER COLUMN id SET DEFAULT nextval('public.recovery_credentials_id_seq'::regclass);


--
-- Name: robot_reservations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations ALTER COLUMN id SET DEFAULT nextval('public.robot_reservations_id_seq'::regclass);


--
-- Name: robot_routes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes ALTER COLUMN id SET DEFAULT nextval('public.robot_routes_id_seq'::regclass);


--
-- Name: robot_telemetry id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry ALTER COLUMN id SET DEFAULT nextval('public.robot_telemetry_id_seq'::regclass);


--
-- Name: robots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots ALTER COLUMN id SET DEFAULT nextval('public.robots_id_seq'::regclass);


--
-- Name: scenarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios ALTER COLUMN id SET DEFAULT nextval('public.scenarios_id_seq'::regclass);


--
-- Name: shrinkage_flags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shrinkage_flags ALTER COLUMN id SET DEFAULT nextval('public.shrinkage_flags_id_seq'::regclass);


--
-- Name: simulation_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events ALTER COLUMN id SET DEFAULT nextval('public.simulation_events_id_seq'::regclass);


--
-- Name: simulation_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots ALTER COLUMN id SET DEFAULT nextval('public.simulation_snapshots_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN id SET DEFAULT nextval('public.stock_movements_id_seq'::regclass);


--
-- Name: system_health_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health_snapshots ALTER COLUMN id SET DEFAULT nextval('public.system_health_snapshots_id_seq'::regclass);


--
-- Name: system_incidents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_incidents ALTER COLUMN id SET DEFAULT nextval('public.system_incidents_id_seq'::regclass);


--
-- Name: task_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events ALTER COLUMN id SET DEFAULT nextval('public.task_events_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: user_warehouse_access id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access ALTER COLUMN id SET DEFAULT nextval('public.user_warehouse_access_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: warehouse_grid_cells id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells ALTER COLUMN id SET DEFAULT nextval('public.warehouse_grid_cells_id_seq'::regclass);


--
-- Name: warehouse_obstacles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles ALTER COLUMN id SET DEFAULT nextval('public.warehouse_obstacles_id_seq'::regclass);


--
-- Data for Name: access_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.access_log (id, "timestamp", username, warehouse_id, action, ip_address) FROM stdin;
378	2026-08-17 18:08:37.608634	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.172
379	2026-08-18 03:55:37.608634	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.179
380	2026-08-19 00:12:37.608634	admin	WH-BOM-01	view	192.168.1.177
381	2026-08-16 09:23:37.608634	admin	WH-BLR-01	view	192.168.1.124
382	2026-08-18 01:16:37.608634	admin	WH-CHN-01	view	192.168.1.208
383	2026-08-19 16:36:37.608634	admin		login	192.168.1.160
384	2026-08-17 08:56:37.608634	harsha200797@gmail.com	WH-DEL-01	view	192.168.1.95
385	2026-08-19 07:10:37.608634	harsha200797@gmail.com	WH-BLR-01	view	192.168.1.63
386	2026-08-19 11:01:37.608634	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.185
387	2026-08-18 15:43:37.608634	harsha200797@gmail.com		login	192.168.1.125
388	2026-08-16 20:19:37.608634	admin	WH-BLR-01	view	192.168.1.104
389	2026-08-17 11:56:37.608634	admin	WH-BLR-01	add_stock	192.168.1.233
390	2026-08-18 21:48:37.608634	harsha200797@gmail.com		login	192.168.1.214
391	2026-08-17 20:49:37.608634	harsha200797@gmail.com	WH-BLR-01	view	192.168.1.59
392	2026-08-17 18:22:37.608634	harsha200797@gmail.com	WH-CHN-01	view	192.168.1.125
393	2026-08-18 02:03:37.608634	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.76
394	2026-08-17 08:46:37.608634	admin		login	192.168.1.137
395	2026-08-19 17:45:37.608634	admin		login	192.168.1.75
396	2026-08-19 17:52:37.608634	harsha200797@gmail.com	WH-CHN-01	view	192.168.1.46
397	2026-08-18 17:05:37.608634	harsha200797@gmail.com	WH-CHN-01	add_stock	192.168.1.14
398	2026-08-18 13:14:37.608634	harsha200797@gmail.com		login	192.168.1.230
399	2026-08-19 04:07:37.608634	admin		login	192.168.1.77
400	2026-08-17 00:51:37.608634	harsha200797@gmail.com	WH-BLR-01	view	192.168.1.229
401	2026-08-17 07:01:37.608634	harsha200797@gmail.com		login	192.168.1.55
402	2026-08-19 13:25:37.608634	harsha200797@gmail.com	WH-BLR-01	view	192.168.1.176
403	2026-08-17 14:30:37.608634	admin	WH-DEL-01	view	192.168.1.73
404	2026-08-17 01:08:37.608634	admin	WH-CCU-01	add_stock	192.168.1.201
405	2026-08-16 18:31:37.608634	admin	WH-DEL-01	view	192.168.1.144
406	2026-08-18 03:51:37.608634	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.92
407	2026-08-19 13:06:37.608634	harsha200797@gmail.com	WH-CHN-01	view	192.168.1.115
408	2026-08-19 02:12:37.608634	admin		login	192.168.1.162
409	2026-08-18 15:54:37.608634	harsha200797@gmail.com	WH-CCU-01	view	192.168.1.235
410	2026-08-17 16:35:37.609636	harsha200797@gmail.com	WH-CHN-01	add_stock	192.168.1.176
411	2026-08-16 17:25:37.609636	admin	WH-BLR-01	view	192.168.1.227
412	2026-08-18 16:07:37.609636	admin	WH-BLR-01	view	192.168.1.91
413	2026-08-17 12:37:37.609636	harsha200797@gmail.com	WH-CCU-01	view	192.168.1.8
414	2026-08-18 02:10:37.609636	harsha200797@gmail.com	WH-CCU-01	view	192.168.1.192
415	2026-08-18 04:50:37.609636	admin	WH-BOM-01	view	192.168.1.196
416	2026-08-18 21:18:37.609636	admin	WH-BLR-01	view	192.168.1.67
417	2026-08-19 14:17:37.609636	admin	WH-BOM-01	view	192.168.1.245
418	2026-08-18 23:51:37.609636	harsha200797@gmail.com	WH-DEL-01	view	192.168.1.96
419	2026-08-16 19:43:37.609636	harsha200797@gmail.com	WH-BLR-01	view	192.168.1.253
420	2026-08-16 10:58:37.609636	admin	WH-BOM-01	view	192.168.1.239
421	2026-08-19 06:44:37.609636	harsha200797@gmail.com	WH-BOM-01	view	192.168.1.231
422	2026-08-19 12:29:37.609636	admin	WH-BOM-01	view	192.168.1.70
423	2026-08-17 10:44:37.609636	admin	WH-BOM-01	add_stock	192.168.1.199
424	2026-08-17 00:51:37.609636	harsha200797@gmail.com	WH-BLR-01	add_stock	192.168.1.95
425	2026-08-19 03:25:37.609636	admin	WH-DEL-01	add_stock	192.168.1.201
426	2026-08-16 20:06:37.609636	admin		login	192.168.1.16
427	2026-08-17 02:57:37.609636	harsha200797@gmail.com		login	192.168.1.98
428	2026-08-19 18:18:42.463285	test_admin_hardened		login	testclient
432	2026-08-19 18:19:10.673528	test_admin_hardened		login	testclient
434	2026-08-19 18:19:11.641012	test_admin_hardened		login	testclient
435	2026-08-19 18:19:19.45818	test_ai_manager		login	testclient
429	2026-08-19 18:18:55.004455	test_admin_hardened		login	testclient
430	2026-08-19 18:19:02.37435	test_admin_hardened		login	testclient
431	2026-08-19 18:19:09.722798	test_admin_hardened		login	testclient
433	2026-08-19 18:19:10.748508	test_admin_hardened	WH-BLR-01	approve_recommendation	testclient
\.


--
-- Data for Name: ai_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_recommendations (id, "timestamp", warehouse_id, item_id, title, risk_level, action_recommended, confidence_score, input_factors, status, decision_by, decision_time, notes, recommendation_type, description, priority, score, confidence_or_reliability, source_model, source_entity_type, source_entity_id, recommended_action, estimated_impact, explanation, supporting_metrics, created_at, reviewed_at, reviewed_by, review_notes, expires_at, metadata) FROM stdin;
9	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	46	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 143.0 units, but recorded stock is 143.0 units, leading to a discrepancy of +0.0 units.	LOW	46	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 143.0, "actual": 143.0, "evidence": ["Expected closing stock: 143.0 units (Opening + In - Out)", "Recorded closing stock: 143.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
13	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	43	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 42.0 units, but recorded stock is 42.0 units, leading to a discrepancy of +0.0 units.	LOW	43	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 42.0, "actual": 42.0, "evidence": ["Expected closing stock: 42.0 units (Opening + In - Out)", "Recorded closing stock: 42.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
21	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	41	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 87.0 units, but recorded stock is 87.0 units, leading to a discrepancy of +0.0 units.	LOW	41	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 87.0, "actual": 87.0, "evidence": ["Expected closing stock: 87.0 units (Opening + In - Out)", "Recorded closing stock: 87.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
27	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	39	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 98.0 units, but recorded stock is 98.0 units, leading to a discrepancy of +0.0 units.	LOW	39	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 98.0, "actual": 98.0, "evidence": ["Expected closing stock: 98.0 units (Opening + In - Out)", "Recorded closing stock: 98.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
28	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 73.0 units, but recorded stock is 73.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 73.0, "actual": 73.0, "evidence": ["Expected closing stock: 73.0 units (Opening + In - Out)", "Recorded closing stock: 73.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
36	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 56.0 units, but recorded stock is 56.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 56.0, "actual": 56.0, "evidence": ["Expected closing stock: 56.0 units (Opening + In - Out)", "Recorded closing stock: 56.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
38	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 28.0 units, but recorded stock is 28.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 28.0, "actual": 28.0, "evidence": ["Expected closing stock: 28.0 units (Opening + In - Out)", "Recorded closing stock: 28.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
39	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 86.0 units, but recorded stock is 86.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 44/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 86.0, "actual": 86.0, "evidence": ["Expected closing stock: 86.0 units (Opening + In - Out)", "Recorded closing stock: 86.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 44/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
45	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 104.0 units, but recorded stock is 104.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 104.0, "actual": 104.0, "evidence": ["Expected closing stock: 104.0 units (Opening + In - Out)", "Recorded closing stock: 104.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
46	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 58.0 units, but recorded stock is 58.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 41/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 58.0, "actual": 58.0, "evidence": ["Expected closing stock: 58.0 units (Opening + In - Out)", "Recorded closing stock: 58.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 41/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
53	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 90.0 units, but recorded stock is 90.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 90.0, "actual": 90.0, "evidence": ["Expected closing stock: 90.0 units (Opening + In - Out)", "Recorded closing stock: 90.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
54	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 230.0 units, but recorded stock is 230.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 230.0, "actual": 230.0, "evidence": ["Expected closing stock: 230.0 units (Opening + In - Out)", "Recorded closing stock: 230.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
70	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 45.0 units, but recorded stock is 45.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 37/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 45.0, "actual": 45.0, "evidence": ["Expected closing stock: 45.0 units (Opening + In - Out)", "Recorded closing stock: 45.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 37/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
72	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-RAM-01	Replenishment Recommended: Corsair DDR5 32GB 6000MHz RAM	MEDIUM	Replenish 75 units.	65	{}	NEW		\N		REPLENISHMENT	Projected lead demand (41.1 units) and safety stock (25 units) exceeds available stock (48 units).	MEDIUM	72	MEDIUM	Weekday Seasonality Regression	Item	ITM-RAM-01	Replenish 75 units.	153850	Outbound demand forecast (41.1 units) indicates available stock (48 units) will deplete below safety stock target (25 units) within lead time of 4 days. WAPE forecast reliability stands at 65%.	{"current_stock": 48, "lead_demand": 41.1, "safety_stock": 25, "reorder_point": 66.1, "shortage_qty": 18.1, "unit_cost": 8500.0, "wape": 45.8, "evidence": ["Current closing stock: 48 units (ACTUAL \\u2014 MySQL)", "Safety stock threshold: 25 units", "Forecasted 4-day lead demand: 41.1 units (FORECAST \\u2014 ML MODEL)", "Reorder point threshold: 66.1 units"]}	2026-08-19 18:18:47.336481	\N	\N	\N	\N	{}
18	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	41	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 29.0 units, but recorded stock is 29.0 units, leading to a discrepancy of +0.0 units.	LOW	41	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 29.0, "actual": 29.0, "evidence": ["Expected closing stock: 29.0 units (Opening + In - Out)", "Recorded closing stock: 29.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
73	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-RAM-01	Replenishment Recommended: Corsair DDR5 32GB 6000MHz RAM	MEDIUM	Replenish 75 units.	45	{}	NEW		\N		REPLENISHMENT	Projected lead demand (24.6 units) and safety stock (25 units) exceeds available stock (44 units).	MEDIUM	57	MEDIUM	Weekday Seasonality Regression	Item	ITM-RAM-01	Replenish 75 units.	47600	Outbound demand forecast (24.6 units) indicates available stock (44 units) will deplete below safety stock target (25 units) within lead time of 4 days. WAPE forecast reliability stands at 45%.	{"current_stock": 44, "lead_demand": 24.6, "safety_stock": 25, "reorder_point": 49.6, "shortage_qty": 5.6, "unit_cost": 8500.0, "wape": 27.2, "evidence": ["Current closing stock: 44 units (ACTUAL \\u2014 MySQL)", "Safety stock threshold: 25 units", "Forecasted 4-day lead demand: 24.6 units (FORECAST \\u2014 ML MODEL)", "Reorder point threshold: 49.6 units"]}	2026-08-19 18:18:47.336481	\N	\N	\N	\N	{}
23	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	40	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 298.0 units, but recorded stock is 298.0 units, leading to a discrepancy of +0.0 units.	LOW	40	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 298.0, "actual": 298.0, "evidence": ["Expected closing stock: 298.0 units (Opening + In - Out)", "Recorded closing stock: 298.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
24	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	39	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 63.0 units, but recorded stock is 63.0 units, leading to a discrepancy of +0.0 units.	LOW	39	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 63.0, "actual": 63.0, "evidence": ["Expected closing stock: 63.0 units (Opening + In - Out)", "Recorded closing stock: 63.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
25	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	39	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 86.0 units, but recorded stock is 86.0 units, leading to a discrepancy of +0.0 units.	LOW	39	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 86.0, "actual": 86.0, "evidence": ["Expected closing stock: 86.0 units (Opening + In - Out)", "Recorded closing stock: 86.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
29	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 74.0 units, but recorded stock is 74.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 74.0, "actual": 74.0, "evidence": ["Expected closing stock: 74.0 units (Opening + In - Out)", "Recorded closing stock: 74.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
30	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 67.0 units, but recorded stock is 67.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 67.0, "actual": 67.0, "evidence": ["Expected closing stock: 67.0 units (Opening + In - Out)", "Recorded closing stock: 67.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
63	2026-08-19 16:53:54.865725	WH-BLR-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 66.0 units, but recorded stock is 66.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 66.0, "actual": 66.0, "evidence": ["Expected closing stock: 66.0 units (Opening + In - Out)", "Recorded closing stock: 66.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
6	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	48	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 89.0 units, but recorded stock is 89.0 units, leading to a discrepancy of +0.0 units.	LOW	48	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 89.0, "actual": 89.0, "evidence": ["Expected closing stock: 89.0 units (Opening + In - Out)", "Recorded closing stock: 89.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
7	2026-08-19 18:19:11.694938	WH-DEL-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	47	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 438.0 units, but recorded stock is 438.0 units, leading to a discrepancy of +0.0 units.	LOW	47	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 37/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 438.0, "actual": 438.0, "evidence": ["Expected closing stock: 438.0 units (Opening + In - Out)", "Recorded closing stock: 438.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 37/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
10	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	45	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 87.0 units, but recorded stock is 87.0 units, leading to a discrepancy of +0.0 units.	LOW	45	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 87.0, "actual": 87.0, "evidence": ["Expected closing stock: 87.0 units (Opening + In - Out)", "Recorded closing stock: 87.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
12	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	43	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 435.0 units, but recorded stock is 435.0 units, leading to a discrepancy of +0.0 units.	LOW	43	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 435.0, "actual": 435.0, "evidence": ["Expected closing stock: 435.0 units (Opening + In - Out)", "Recorded closing stock: 435.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
16	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	42	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 211.0 units, but recorded stock is 211.0 units, leading to a discrepancy of +0.0 units.	LOW	42	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 211.0, "actual": 211.0, "evidence": ["Expected closing stock: 211.0 units (Opening + In - Out)", "Recorded closing stock: 211.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
51	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 44.0 units, but recorded stock is 44.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 44.0, "actual": 44.0, "evidence": ["Expected closing stock: 44.0 units (Opening + In - Out)", "Recorded closing stock: 44.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
52	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 43.0 units, but recorded stock is 43.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 43.0, "actual": 43.0, "evidence": ["Expected closing stock: 43.0 units (Opening + In - Out)", "Recorded closing stock: 43.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
2	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	HIGH	Perform physical stock audit count and check transaction logs.	51	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 45.0 units, but recorded stock is 45.0 units, leading to a discrepancy of +0.0 units.	HIGH	51	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 45.0, "actual": 45.0, "evidence": ["Expected closing stock: 45.0 units (Opening + In - Out)", "Recorded closing stock: 45.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
4	2026-08-19 18:19:11.694938	WH-BOM-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	49	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 109.0 units, but recorded stock is 109.0 units, leading to a discrepancy of +0.0 units.	LOW	49	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 109.0, "actual": 109.0, "evidence": ["Expected closing stock: 109.0 units (Opening + In - Out)", "Recorded closing stock: 109.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
1	2026-08-19 18:19:02.428147	WH-BLR-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	MEDIUM	Perform physical stock audit count and check transaction logs.	52	{}	APPROVED		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 294.0 units, but recorded stock is 294.0 units, leading to a discrepancy of +0.0 units.	MEDIUM	52	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 294.0, "actual": 294.0, "evidence": ["Expected closing stock: 294.0 units (Opening + In - Out)", "Recorded closing stock: 294.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	2026-08-19 18:19:10.73832	test_admin_hardened	Test approval	\N	{}
8	2026-08-19 16:43:34.533228	WH-CCU-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	46	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 60.0 units, but recorded stock is 60.0 units, leading to a discrepancy of +0.0 units.	LOW	46	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 60.0, "actual": 60.0, "evidence": ["Expected closing stock: 60.0 units (Opening + In - Out)", "Recorded closing stock: 60.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
11	2026-08-19 16:43:34.533228	WH-BOM-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	44	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 65.0 units, but recorded stock is 65.0 units, leading to a discrepancy of +0.0 units.	LOW	44	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 65.0, "actual": 65.0, "evidence": ["Expected closing stock: 65.0 units (Opening + In - Out)", "Recorded closing stock: 65.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
14	2026-08-19 16:43:34.533228	WH-BLR-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	HIGH	Perform physical stock audit count and check transaction logs.	42	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 34.0 units, but recorded stock is 34.0 units, leading to a discrepancy of +0.0 units.	HIGH	42	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 41/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 34.0, "actual": 34.0, "evidence": ["Expected closing stock: 34.0 units (Opening + In - Out)", "Recorded closing stock: 34.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 41/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
15	2026-08-19 16:43:34.533228	WH-BOM-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	42	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 67.0 units, but recorded stock is 67.0 units, leading to a discrepancy of +0.0 units.	LOW	42	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 67.0, "actual": 67.0, "evidence": ["Expected closing stock: 67.0 units (Opening + In - Out)", "Recorded closing stock: 67.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
19	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	41	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 75.0 units, but recorded stock is 75.0 units, leading to a discrepancy of +0.0 units.	LOW	41	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 75.0, "actual": 75.0, "evidence": ["Expected closing stock: 75.0 units (Opening + In - Out)", "Recorded closing stock: 75.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
17	2026-08-19 16:43:34.533228	WH-BLR-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	41	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 42.0 units, but recorded stock is 42.0 units, leading to a discrepancy of +0.0 units.	LOW	41	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 42.0, "actual": 42.0, "evidence": ["Expected closing stock: 42.0 units (Opening + In - Out)", "Recorded closing stock: 42.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
20	2026-08-19 18:19:11.694938	WH-CCU-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	41	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 29.0 units, but recorded stock is 29.0 units, leading to a discrepancy of +0.0 units.	LOW	41	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 29.0, "actual": 29.0, "evidence": ["Expected closing stock: 29.0 units (Opening + In - Out)", "Recorded closing stock: 29.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
22	2026-08-19 16:43:34.533228	WH-BOM-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	40	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 438.0 units, but recorded stock is 438.0 units, leading to a discrepancy of +0.0 units.	LOW	40	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 40/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 438.0, "actual": 438.0, "evidence": ["Expected closing stock: 438.0 units (Opening + In - Out)", "Recorded closing stock: 438.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 40/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
42	2026-08-19 16:43:34.533228	WH-CCU-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 17.0 units, but recorded stock is 17.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 17.0, "actual": 17.0, "evidence": ["Expected closing stock: 17.0 units (Opening + In - Out)", "Recorded closing stock: 17.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
50	2026-08-19 16:43:34.533228	WH-CCU-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 45.0 units, but recorded stock is 45.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 45.0, "actual": 45.0, "evidence": ["Expected closing stock: 45.0 units (Opening + In - Out)", "Recorded closing stock: 45.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
3	2026-08-19 16:43:34.533228	WH-BLR-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	49	{}	DISMISSED		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 66.0 units, but recorded stock is 66.0 units, leading to a discrepancy of +0.0 units.	LOW	49	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 66.0, "actual": 66.0, "evidence": ["Expected closing stock: 66.0 units (Opening + In - Out)", "Recorded closing stock: 66.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
26	2026-08-19 16:44:01.525614	WH-CHN-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	39	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 141.0 units, but recorded stock is 141.0 units, leading to a discrepancy of +0.0 units.	LOW	39	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 141.0, "actual": 141.0, "evidence": ["Expected closing stock: 141.0 units (Opening + In - Out)", "Recorded closing stock: 141.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
31	2026-08-19 16:44:01.525614	WH-CCU-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 276.0 units, but recorded stock is 276.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 276.0, "actual": 276.0, "evidence": ["Expected closing stock: 276.0 units (Opening + In - Out)", "Recorded closing stock: 276.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
33	2026-08-19 16:44:01.525614	WH-DEL-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 293.0 units, but recorded stock is 293.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 293.0, "actual": 293.0, "evidence": ["Expected closing stock: 293.0 units (Opening + In - Out)", "Recorded closing stock: 293.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
61	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 294.0 units, but recorded stock is 294.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 294.0, "actual": 294.0, "evidence": ["Expected closing stock: 294.0 units (Opening + In - Out)", "Recorded closing stock: 294.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
62	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 142.0 units, but recorded stock is 142.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 142.0, "actual": 142.0, "evidence": ["Expected closing stock: 142.0 units (Opening + In - Out)", "Recorded closing stock: 142.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
67	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 83.0 units, but recorded stock is 83.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 83.0, "actual": 83.0, "evidence": ["Expected closing stock: 83.0 units (Opening + In - Out)", "Recorded closing stock: 83.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
64	2026-08-19 16:44:01.525614	WH-BOM-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 87.0 units, but recorded stock is 87.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 87.0, "actual": 87.0, "evidence": ["Expected closing stock: 87.0 units (Opening + In - Out)", "Recorded closing stock: 87.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
69	2026-08-19 16:44:01.525614	WH-CHN-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 61.0 units, but recorded stock is 61.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 61.0, "actual": 61.0, "evidence": ["Expected closing stock: 61.0 units (Opening + In - Out)", "Recorded closing stock: 61.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
37	2026-08-19 18:18:55.06306	WH-BLR-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 142.0 units, but recorded stock is 142.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 142.0, "actual": 142.0, "evidence": ["Expected closing stock: 142.0 units (Opening + In - Out)", "Recorded closing stock: 142.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
40	2026-08-19 18:18:55.06306	WH-BOM-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 109.0 units, but recorded stock is 109.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 109.0, "actual": 109.0, "evidence": ["Expected closing stock: 109.0 units (Opening + In - Out)", "Recorded closing stock: 109.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
41	2026-08-19 18:18:55.06306	WH-CCU-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 75.0 units, but recorded stock is 75.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 75.0, "actual": 75.0, "evidence": ["Expected closing stock: 75.0 units (Opening + In - Out)", "Recorded closing stock: 75.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
43	2026-08-19 18:18:55.06306	WH-CCU-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 29.0 units, but recorded stock is 29.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 29.0, "actual": 29.0, "evidence": ["Expected closing stock: 29.0 units (Opening + In - Out)", "Recorded closing stock: 29.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
55	2026-08-19 18:18:55.06306	WH-CHN-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 45.0 units, but recorded stock is 45.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 45.0, "actual": 45.0, "evidence": ["Expected closing stock: 45.0 units (Opening + In - Out)", "Recorded closing stock: 45.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
44	2026-08-19 18:19:11.694938	WH-CHN-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	37	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 44.0 units, but recorded stock is 44.0 units, leading to a discrepancy of +0.0 units.	LOW	37	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 37/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 44.0, "actual": 44.0, "evidence": ["Expected closing stock: 44.0 units (Opening + In - Out)", "Recorded closing stock: 44.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 37/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
5	2026-08-19 18:19:02.428147	WH-BLR-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	48	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 58.0 units, but recorded stock is 58.0 units, leading to a discrepancy of +0.0 units.	LOW	48	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 41/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 58.0, "actual": 58.0, "evidence": ["Expected closing stock: 58.0 units (Opening + In - Out)", "Recorded closing stock: 58.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 41/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
32	2026-08-19 18:19:02.428147	WH-CHN-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 83.0 units, but recorded stock is 83.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 83.0, "actual": 83.0, "evidence": ["Expected closing stock: 83.0 units (Opening + In - Out)", "Recorded closing stock: 83.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
34	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-CPU-01	Review Inventory Anomaly: AMD Ryzen 9 7900X Processor	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 45.0 units, but recorded stock is 45.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 37/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 45.0, "actual": 45.0, "evidence": ["Expected closing stock: 45.0 units (Opening + In - Out)", "Recorded closing stock: 45.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 37/100 (ML MODEL)", "Unit Cost: \\u20b938,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
35	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	38	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 42.0 units, but recorded stock is 42.0 units, leading to a discrepancy of +0.0 units.	LOW	38	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 42.0, "actual": 42.0, "evidence": ["Expected closing stock: 42.0 units (Opening + In - Out)", "Recorded closing stock: 42.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
47	2026-08-19 18:19:02.428147	WH-BLR-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 73.0 units, but recorded stock is 73.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 73.0, "actual": 73.0, "evidence": ["Expected closing stock: 73.0 units (Opening + In - Out)", "Recorded closing stock: 73.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
48	2026-08-19 18:19:02.428147	WH-BOM-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 28.0 units, but recorded stock is 28.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 28.0, "actual": 28.0, "evidence": ["Expected closing stock: 28.0 units (Opening + In - Out)", "Recorded closing stock: 28.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
49	2026-08-19 18:19:02.428147	WH-BOM-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 86.0 units, but recorded stock is 86.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 44/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 86.0, "actual": 86.0, "evidence": ["Expected closing stock: 86.0 units (Opening + In - Out)", "Recorded closing stock: 86.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 44/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
56	2026-08-19 18:19:02.428147	WH-CHN-01	ITM-GPU-01	Review Inventory Anomaly: Nvidia RTX 4080 Founders Edition	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 44.0 units, but recorded stock is 44.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-GPU-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 37/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 44.0, "actual": 44.0, "evidence": ["Expected closing stock: 44.0 units (Opening + In - Out)", "Recorded closing stock: 44.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 37/100 (ML MODEL)", "Unit Cost: \\u20b995,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
57	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-CHG-01	Review Inventory Anomaly: Anker 100W GaN Wall Charger	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 143.0 units, but recorded stock is 143.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CHG-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 143.0, "actual": 143.0, "evidence": ["Expected closing stock: 143.0 units (Opening + In - Out)", "Recorded closing stock: 143.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b92,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
58	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-HDD-01	Review Inventory Anomaly: WD Red Pro 8TB NAS Hard Drive	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 87.0 units, but recorded stock is 87.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-HDD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 87.0, "actual": 87.0, "evidence": ["Expected closing stock: 87.0 units (Opening + In - Out)", "Recorded closing stock: 87.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b916,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
59	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 104.0 units, but recorded stock is 104.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 39/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 104.0, "actual": 104.0, "evidence": ["Expected closing stock: 104.0 units (Opening + In - Out)", "Recorded closing stock: 104.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 39/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
60	2026-08-19 18:19:02.428147	WH-DEL-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	36	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 56.0 units, but recorded stock is 56.0 units, leading to a discrepancy of +0.0 units.	LOW	36	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 56.0, "actual": 56.0, "evidence": ["Expected closing stock: 56.0 units (Opening + In - Out)", "Recorded closing stock: 56.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
65	2026-08-19 18:19:02.428147	WH-CCU-01	ITM-SSD-01	Review Inventory Anomaly: Samsung 990 Pro 2TB NVMe SSD	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 90.0 units, but recorded stock is 90.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-SSD-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 38/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 90.0, "actual": 90.0, "evidence": ["Expected closing stock: 90.0 units (Opening + In - Out)", "Recorded closing stock: 90.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 38/100 (ML MODEL)", "Unit Cost: \\u20b912,000.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
66	2026-08-19 18:19:02.428147	WH-CHN-01	ITM-CBL-01	Review Inventory Anomaly: Apple USB-C Braided Cable 2m	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 230.0 units, but recorded stock is 230.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-CBL-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 36/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 230.0, "actual": 230.0, "evidence": ["Expected closing stock: 230.0 units (Opening + In - Out)", "Recorded closing stock: 230.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 36/100 (ML MODEL)", "Unit Cost: \\u20b9800.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
68	2026-08-19 18:19:02.428147	WH-CHN-01	ITM-RAM-01	Review Inventory Anomaly: Corsair DDR5 32GB 6000MHz RAM	LOW	Perform physical stock audit count and check transaction logs.	35	{}	NEW		\N		ANOMALY	Recorded inventory mismatch. Expected closing stock was 98.0 units, but recorded stock is 98.0 units, leading to a discrepancy of +0.0 units.	LOW	35	HIGH	IsolationForest 2.0 Anomaly Detection	ShrinkageFlag	ITM-RAM-01	Perform physical stock audit count and check transaction logs.	0	IsolationForest anomaly detector identified an atypical discrepancies signature (Score: 35/100) on recorded stock movements. Note: This flags potential discrepancies requiring physical recount, not confirmed theft.	{"discrepancy": 0.0, "expected": 98.0, "actual": 98.0, "evidence": ["Expected closing stock: 98.0 units (Opening + In - Out)", "Recorded closing stock: 98.0 units (ACTUAL \\u2014 MySQL)", "Inventory discrepancy: +0.0 units (CALCULATED)", "Investigation priority score: 35/100 (ML MODEL)", "Unit Cost: \\u20b98,500.00 -> Estimated Exposure: \\u20b90.00 (CALCULATED)"]}	2026-08-19 16:43:21.322437	\N	\N	\N	\N	{}
71	2026-08-19 18:19:11.694938	WH-BLR-01	ITM-RAM-01	Replenishment Recommended: Corsair DDR5 32GB 6000MHz RAM	MEDIUM	Replenish 75 units.	50	{}	NEW		\N		REPLENISHMENT	Projected lead demand (42.0 units) and safety stock (25 units) exceeds available stock (44 units).	MEDIUM	78	MEDIUM	Weekday Seasonality Regression	Item	ITM-RAM-01	Replenish 75 units.	195500	Outbound demand forecast (42.0 units) indicates available stock (44 units) will deplete below safety stock target (25 units) within lead time of 4 days. WAPE forecast reliability stands at 50%.	{"current_stock": 44, "lead_demand": 42.0, "safety_stock": 25, "reorder_point": 67.0, "shortage_qty": 23.0, "unit_cost": 8500.0, "wape": 29.6, "evidence": ["Current closing stock: 44 units (ACTUAL \\u2014 MySQL)", "Safety stock threshold: 25 units", "Forecasted 4-day lead demand: 42.0 units (FORECAST \\u2014 ML MODEL)", "Reorder point threshold: 67.0 units"]}	2026-08-19 18:18:47.336481	\N	\N	\N	\N	{}
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
c6a0f47c242e
\.


--
-- Data for Name: audit_ledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_ledger (id, "timestamp", event_type, details, prev_hash, hash) FROM stdin;
1	2026-08-19 15:43:05	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	0000000000000000000000000000000000000000000000000000000000000000	ad8f32f19d808d29b5e73d8e1bf9d53a57893633451c53ce715768c395f9d712
2	2026-08-19 15:43:05	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	ad8f32f19d808d29b5e73d8e1bf9d53a57893633451c53ce715768c395f9d712	af8de1d7d027b3020dcc1e59b62383f479caefa82802bb22cafc3e64c414c321
3	2026-08-19 15:43:05	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	af8de1d7d027b3020dcc1e59b62383f479caefa82802bb22cafc3e64c414c321	1e1c20d52a81e3cd3b3749813ebd9d44a6d3cabf7911b594f94073d3a92569c1
4	2026-08-19 15:43:05	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	1e1c20d52a81e3cd3b3749813ebd9d44a6d3cabf7911b594f94073d3a92569c1	03ce28ea0c5ad75008e2432fc8731871d134ba1932be4adf8ac3fab220bd22be
5	2026-08-19 15:43:05	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	03ce28ea0c5ad75008e2432fc8731871d134ba1932be4adf8ac3fab220bd22be	3083c8d5f46b94e698d0be7d99b93f217f6b2c4352869d46403b1ea75812c6e0
6	2026-08-19 15:43:05	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	3083c8d5f46b94e698d0be7d99b93f217f6b2c4352869d46403b1ea75812c6e0	a18c6092eebbe3460d17d59417ed663527ed88da795621efc58ce9e2094c66ba
7	2026-08-19 15:43:05	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	a18c6092eebbe3460d17d59417ed663527ed88da795621efc58ce9e2094c66ba	645525b762fda241e15d71d22d190b5da040adefa06db807e95f63c9a3df44da
8	2026-08-19 15:43:05	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	645525b762fda241e15d71d22d190b5da040adefa06db807e95f63c9a3df44da	17a9ba9597e2df82351aa4558bcffa1e6f3fa66948139a6dc81ce68a5cbef0c1
9	2026-08-19 15:43:05	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	17a9ba9597e2df82351aa4558bcffa1e6f3fa66948139a6dc81ce68a5cbef0c1	d6b9c34f9e94709534807d27d5e4d4fcc9aa0d36c6638b2396dafdfd71c12d89
10	2026-08-19 15:43:05	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	d6b9c34f9e94709534807d27d5e4d4fcc9aa0d36c6638b2396dafdfd71c12d89	9a5436b3dcca4d7a1e7a6be1096e2c93f4d0ae1b43456d8319c187a11dc6182c
11	2026-08-19 15:43:05	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	9a5436b3dcca4d7a1e7a6be1096e2c93f4d0ae1b43456d8319c187a11dc6182c	4f8ea912a895a05940e79a477b492479fb6ff152a498fc5151660cacdea79d68
12	2026-08-19 15:43:05	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	4f8ea912a895a05940e79a477b492479fb6ff152a498fc5151660cacdea79d68	3ac26c8b0e3e33426813b86a35622d7d439e094a40b8e2ffcde0582b8d8fdcf4
13	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-18"}	3ac26c8b0e3e33426813b86a35622d7d439e094a40b8e2ffcde0582b8d8fdcf4	944dabfc806eb8b3fffd8c648fef66870a5b61dcba504eb7fe83196b1ce04557
14	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	944dabfc806eb8b3fffd8c648fef66870a5b61dcba504eb7fe83196b1ce04557	eba0041f5eacbdfff13598abe79cc05218c6f982014aebb0396ed7dc1cc2ad58
15	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	eba0041f5eacbdfff13598abe79cc05218c6f982014aebb0396ed7dc1cc2ad58	8086601575c3acccb7372c1b9ece4006ca95881dafb73f73d4f3ee42a8852b7f
16	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	8086601575c3acccb7372c1b9ece4006ca95881dafb73f73d4f3ee42a8852b7f	fe600e1fa700c032f051a01306bc674bb9a49798e43d08bea038927fd5b101bc
17	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	fe600e1fa700c032f051a01306bc674bb9a49798e43d08bea038927fd5b101bc	06afd9cc4776e31691a6cb7f2f34f1c06704527366d382f705642a6c5d1afdb7
18	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	06afd9cc4776e31691a6cb7f2f34f1c06704527366d382f705642a6c5d1afdb7	bfb20aa0253e56ece247dde17b703cc312b8ab100624059b70bcb0c421953ecf
19	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	bfb20aa0253e56ece247dde17b703cc312b8ab100624059b70bcb0c421953ecf	449081ba33ac56de47da9c5dd31cd055ed98f7c7edc1b38a9a543d77ed702c88
20	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	449081ba33ac56de47da9c5dd31cd055ed98f7c7edc1b38a9a543d77ed702c88	465c2303c176440095fd019732d7723b18cc2fa5abf6078d62c68592df994a30
21	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-07-27"}	465c2303c176440095fd019732d7723b18cc2fa5abf6078d62c68592df994a30	9b61c1db086dae7339463500c2ef371598db9f94ba90c4990a22daf8fea607b4
22	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	9b61c1db086dae7339463500c2ef371598db9f94ba90c4990a22daf8fea607b4	93caeda9185869d0a4501855e9ba6626e9096aa1fb8125f2499994621949d221
23	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	93caeda9185869d0a4501855e9ba6626e9096aa1fb8125f2499994621949d221	b5112af0b8f7060aca3757fb4c10f15231269de68da7ca3ef1517133183998f1
24	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-29"}	b5112af0b8f7060aca3757fb4c10f15231269de68da7ca3ef1517133183998f1	7e5c54a28568bd3fb40c64fe0684151e9efd4f68b3e2f574ed3dd9183d42e966
25	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-30"}	7e5c54a28568bd3fb40c64fe0684151e9efd4f68b3e2f574ed3dd9183d42e966	e6023ec82f565ae70855655d2ad0c017b868ffa30a4cdae41fc5dcb42fdf9b16
26	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-02"}	e6023ec82f565ae70855655d2ad0c017b868ffa30a4cdae41fc5dcb42fdf9b16	cb92ee9dad01ad24fecf3ad3258b5e76655201efaf7aef182133b15909b93a21
27	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	cb92ee9dad01ad24fecf3ad3258b5e76655201efaf7aef182133b15909b93a21	5454186db55b056b61f4c50582d779faffc79f5954228f2cda01c7f5308b3433
28	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	5454186db55b056b61f4c50582d779faffc79f5954228f2cda01c7f5308b3433	1fd7f2759bb6c6a1ac52649deee4b2359eca49c23574b21c31b7c3a9e4464a38
29	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	1fd7f2759bb6c6a1ac52649deee4b2359eca49c23574b21c31b7c3a9e4464a38	3a55218ce975a2081e69a98722173b8990dbecc0a5490c0b61a7ce9ec6015949
30	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-03"}	3a55218ce975a2081e69a98722173b8990dbecc0a5490c0b61a7ce9ec6015949	489f56d1f1431b786bfb1126e62f17b8723d440b16046bd0a726fc760df715c9
31	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	489f56d1f1431b786bfb1126e62f17b8723d440b16046bd0a726fc760df715c9	a9bf8381e585b55d3ba4afabbd062d8520f1b7e6550ec06b5e6e364e2064547a
32	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	a9bf8381e585b55d3ba4afabbd062d8520f1b7e6550ec06b5e6e364e2064547a	3ca47a829b3912859c94aa96d79249f5d2f5f3d028fa0498fd8771aab87f4e04
33	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-04"}	3ca47a829b3912859c94aa96d79249f5d2f5f3d028fa0498fd8771aab87f4e04	d6741aea9415c75d06961ed601a2ab381260376b137f539abec4f1a2165a03d9
34	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-05"}	d6741aea9415c75d06961ed601a2ab381260376b137f539abec4f1a2165a03d9	ef40fb2529d8f918a3502228e55ed94cf3f40c9e7085c92f05e090011da1e318
35	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-05"}	ef40fb2529d8f918a3502228e55ed94cf3f40c9e7085c92f05e090011da1e318	921eecc9e33abaec4ff9f12b5fb1270cc3455bbc1b2b2a2550b30853d1f13565
36	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	921eecc9e33abaec4ff9f12b5fb1270cc3455bbc1b2b2a2550b30853d1f13565	cc48bd54ecca79495cdfda1924bd6c3f8b0bdb7f4e697ff79fa7b0606de2035d
37	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-06"}	cc48bd54ecca79495cdfda1924bd6c3f8b0bdb7f4e697ff79fa7b0606de2035d	3c41ffa52dc328bdfe96ad6e99e8a633832b24d36d0300c7884f494f0d0ecb77
38	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-06"}	3c41ffa52dc328bdfe96ad6e99e8a633832b24d36d0300c7884f494f0d0ecb77	e5f259dbdc314aae695030a73ec2f759b40a1f90383059801c52884bcff9efef
39	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-07"}	e5f259dbdc314aae695030a73ec2f759b40a1f90383059801c52884bcff9efef	67a62198989d1b65ffe1bcd11faec2c0555a4486f50aeb54106da69639ee014b
40	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-07"}	67a62198989d1b65ffe1bcd11faec2c0555a4486f50aeb54106da69639ee014b	8f8c20a208c3b4636796f9cb5cc7e463b3106add03b5da0d5618897171e8a4b2
41	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-07"}	8f8c20a208c3b4636796f9cb5cc7e463b3106add03b5da0d5618897171e8a4b2	0df0bf1fa834fc0abb8f68d915f102cba62875feec3a44234a12d7dee37f1691
42	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	0df0bf1fa834fc0abb8f68d915f102cba62875feec3a44234a12d7dee37f1691	081f3ce3a91618d134d5adc032e0f9ccd598a45023da43e40d4abd53724eb30e
43	2026-08-19 15:43:05	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	081f3ce3a91618d134d5adc032e0f9ccd598a45023da43e40d4abd53724eb30e	40227628558902049b9e4d89052afb7b873268bc652a00c3673eb0f55a8ecedd
44	2026-08-19 15:43:05	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	40227628558902049b9e4d89052afb7b873268bc652a00c3673eb0f55a8ecedd	3e3f0cd60f4ac327bf00deecd93cc897f092bde6d05e91a1f6439f1beea10a7e
45	2026-08-19 15:43:05	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	3e3f0cd60f4ac327bf00deecd93cc897f092bde6d05e91a1f6439f1beea10a7e	9e89fe0d86a79c43efc13ca18bfc9193869c5eae82693089795b8f53a1d9d171
46	2026-08-19 15:43:33	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	9e89fe0d86a79c43efc13ca18bfc9193869c5eae82693089795b8f53a1d9d171	ba65fe818bbd0adc926e9c2076c41d4d256eba7ca56deb84853db58bca9c501f
47	2026-08-19 15:43:33	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	ba65fe818bbd0adc926e9c2076c41d4d256eba7ca56deb84853db58bca9c501f	1ca3693f007403abb572c4a35d59ee33edd38a6983bad5588c768475c6da6bb9
48	2026-08-19 15:43:33	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	1ca3693f007403abb572c4a35d59ee33edd38a6983bad5588c768475c6da6bb9	34f28080db1684fc252ea6de48b6c5e3ef7a29eb8aa4bf804897ce192f92bdaf
49	2026-08-19 15:43:33	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	34f28080db1684fc252ea6de48b6c5e3ef7a29eb8aa4bf804897ce192f92bdaf	1230308457c5d0e80282fa728f232d652562f6e5bfbb5c77a58fa3c5863b6c5c
50	2026-08-19 15:43:33	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	1230308457c5d0e80282fa728f232d652562f6e5bfbb5c77a58fa3c5863b6c5c	2daaa067a4e037390a30d9447a0181b271703f805a7faf0dacd9073efd33f835
51	2026-08-19 15:43:33	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	2daaa067a4e037390a30d9447a0181b271703f805a7faf0dacd9073efd33f835	54db878f1e10ec1f4ca0c68971c125299271e6574d842932ec00e6135f8402f6
52	2026-08-19 15:43:33	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	54db878f1e10ec1f4ca0c68971c125299271e6574d842932ec00e6135f8402f6	aa465291b42a1c3c428e7a9ea2bafe1e97ddb5de68f147ccea026a18b57f8687
53	2026-08-19 15:43:33	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	aa465291b42a1c3c428e7a9ea2bafe1e97ddb5de68f147ccea026a18b57f8687	5b1f506e56aee4fe1ea83c22ebe89d25d6fab3757e4ee95fae4261ca68248660
54	2026-08-19 15:43:33	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	5b1f506e56aee4fe1ea83c22ebe89d25d6fab3757e4ee95fae4261ca68248660	89c478485dd294a9582abde73685f622fee46f775df52315de66ffc95a50a05c
55	2026-08-19 15:43:33	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	89c478485dd294a9582abde73685f622fee46f775df52315de66ffc95a50a05c	66040bc70d1ebe00f9d17739a030e7caff94777043c1ba38a8e950a5f302fcef
56	2026-08-19 15:43:33	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	66040bc70d1ebe00f9d17739a030e7caff94777043c1ba38a8e950a5f302fcef	b28b686689362f51122a368db908ea45c4b6e2ed7f11e5d92e044229b3ae477b
57	2026-08-19 15:43:33	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	b28b686689362f51122a368db908ea45c4b6e2ed7f11e5d92e044229b3ae477b	fc3e771e8b677aae95b9e59b1a66e728e8018c7d878169ff0f744f0b24f5dfd7
58	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	fc3e771e8b677aae95b9e59b1a66e728e8018c7d878169ff0f744f0b24f5dfd7	0bafe849206d8615780bc3ed43a72758b55415f1667d752521a8b7b78e8b8e48
59	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	0bafe849206d8615780bc3ed43a72758b55415f1667d752521a8b7b78e8b8e48	b62be268b15cfed544fcd1dac454a1588fad5f3bd2c8f61187f3dabf3a4e9706
60	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	b62be268b15cfed544fcd1dac454a1588fad5f3bd2c8f61187f3dabf3a4e9706	d5e7f9cec36c1710bd6da575c19193726d56dcaa80f355294c03c826fff2f020
61	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	d5e7f9cec36c1710bd6da575c19193726d56dcaa80f355294c03c826fff2f020	62b70c9b7f8f8c065060801b3e781d73f6057a1ce3e42c79e6dafd69f539378a
62	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	62b70c9b7f8f8c065060801b3e781d73f6057a1ce3e42c79e6dafd69f539378a	a56e4aff66cc5aa4fe8b5ed62db2af9f8e7fe8a910dfa91a9a076d9103060ebb
63	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	a56e4aff66cc5aa4fe8b5ed62db2af9f8e7fe8a910dfa91a9a076d9103060ebb	4be0e683cc32a0d5b77596586982b53cbde64cd6d48d047031ebf7f95971267e
64	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	4be0e683cc32a0d5b77596586982b53cbde64cd6d48d047031ebf7f95971267e	cdd815456d6926c8b2476b7b2ec462e3994e5992d249082d2574dbff296dd09b
65	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	cdd815456d6926c8b2476b7b2ec462e3994e5992d249082d2574dbff296dd09b	9758b784a054efb40c5f64161653e247420a25ee8dd9081e3a2a14670eff6541
66	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	9758b784a054efb40c5f64161653e247420a25ee8dd9081e3a2a14670eff6541	7f9fdc10c95e5554a0dc9cb0e4252fcdcff9a4e4c1b87975d8360e8863eab3a4
67	2026-08-19 15:43:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-29"}	7f9fdc10c95e5554a0dc9cb0e4252fcdcff9a4e4c1b87975d8360e8863eab3a4	06752c46af2ff83c748657f7bef2444648ebfa3e897a4eab6b6c9da410633476
68	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-31"}	06752c46af2ff83c748657f7bef2444648ebfa3e897a4eab6b6c9da410633476	8791ef204737acdea4710e3cb566e2b8284cb9c9f5fee2e83bd0c746a8a7965d
69	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	8791ef204737acdea4710e3cb566e2b8284cb9c9f5fee2e83bd0c746a8a7965d	0bc0d86e10d8f5c45b217e4c9bc6570150be77f2378359ddd1549deef42e5021
70	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	0bc0d86e10d8f5c45b217e4c9bc6570150be77f2378359ddd1549deef42e5021	2fc4adf2f63ca07e1d3e0ce9f13e9941fdde1c243c32bce4ec07dfb433802cb2
71	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	2fc4adf2f63ca07e1d3e0ce9f13e9941fdde1c243c32bce4ec07dfb433802cb2	f58df2d5aee9bb96ee81a2c86484c2345b3cae1fe54ed97c7c7f499961d3205a
72	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	f58df2d5aee9bb96ee81a2c86484c2345b3cae1fe54ed97c7c7f499961d3205a	d71c4692be62dd519a7859a88ce637d551d1f43d67308e28d5d315fb7dee85ac
73	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-08-01"}	d71c4692be62dd519a7859a88ce637d551d1f43d67308e28d5d315fb7dee85ac	cee5afe0794f71781cf31969c1fca78592a6f0e8942d2882408c019bc15825c2
74	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-02"}	cee5afe0794f71781cf31969c1fca78592a6f0e8942d2882408c019bc15825c2	a04a08d31090c85eca47edfdfc0bba7413f8e23904d63c0f8a52a40e21865567
75	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-02"}	a04a08d31090c85eca47edfdfc0bba7413f8e23904d63c0f8a52a40e21865567	271e2880703b2de49e5f7f893e0c5782fcfdb04cdc8e78bc6feb195ee16a71a1
76	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-03"}	271e2880703b2de49e5f7f893e0c5782fcfdb04cdc8e78bc6feb195ee16a71a1	8f91a6f66cfe36138e125a9e2069ee6ca5f6a44ffea23b8b5642136990cd24ec
77	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	8f91a6f66cfe36138e125a9e2069ee6ca5f6a44ffea23b8b5642136990cd24ec	6524c5907c7e86b0e52db3092cbc6505cedf4ee4344b728f5e2715954d2b87b5
78	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-05"}	6524c5907c7e86b0e52db3092cbc6505cedf4ee4344b728f5e2715954d2b87b5	c56ffbfdd8b5f071cb5fe05af798182170410312518ac464182bb9676feeabb7
79	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	c56ffbfdd8b5f071cb5fe05af798182170410312518ac464182bb9676feeabb7	17904977be18f3474d60fd195d6bd7bc500ebbf0cedc151ecbea166bdb509f82
80	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	17904977be18f3474d60fd195d6bd7bc500ebbf0cedc151ecbea166bdb509f82	2dac82f7b191b03d50533fede0517f330ae858c218161613b8d14f79a798fe6e
81	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-06"}	2dac82f7b191b03d50533fede0517f330ae858c218161613b8d14f79a798fe6e	ace66f8fc08be478159eac4ba58b6304015012f902b1327d75b7aa95ca60a475
82	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-07"}	ace66f8fc08be478159eac4ba58b6304015012f902b1327d75b7aa95ca60a475	a8a4b485059f4b5b5105898db8bd609c3936ebd8a26e6aa133c0309e67f77485
83	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-07"}	a8a4b485059f4b5b5105898db8bd609c3936ebd8a26e6aa133c0309e67f77485	e5a1dddf26f5e58ec210643fc9ac49186c75de329ed53ba975cb8e102a5bcddb
84	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-08"}	e5a1dddf26f5e58ec210643fc9ac49186c75de329ed53ba975cb8e102a5bcddb	a7cc87c2248041c130b255558f85bbddd2df858be9038f0aa2e1f1f0b5ec79bb
85	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-09"}	a7cc87c2248041c130b255558f85bbddd2df858be9038f0aa2e1f1f0b5ec79bb	ce9c8edc6a2dc6bf60a40104b2a13b5fafdcce878714aa72608765cbfec23502
112	2026-08-19 15:56:33	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	7086d2e3e6a8e45319c880050c53aa79315cab559d014abea52e1ae9cf433ad1	ab875242ff043ca3ff87cbc285e0f669a4f218a220451b30a3fa22969f36c8e3
86	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-09"}	ce9c8edc6a2dc6bf60a40104b2a13b5fafdcce878714aa72608765cbfec23502	5fd0093c743dfb1c87a9b52fe484754e13e5c138db381f34018f51863367bbae
87	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-09"}	5fd0093c743dfb1c87a9b52fe484754e13e5c138db381f34018f51863367bbae	7ddd39c1b757d9fbbe318b5dcaa5955d750e1a3bc9baf4fd8c2760d2277c2be8
88	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	7ddd39c1b757d9fbbe318b5dcaa5955d750e1a3bc9baf4fd8c2760d2277c2be8	48fb7f12fba4a231fd046a1ebd0aab66914be6cbffea5825470bbaa4a6400713
89	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-10"}	48fb7f12fba4a231fd046a1ebd0aab66914be6cbffea5825470bbaa4a6400713	2d26db42f6c80dbb218324dcf206b9f2250489ef3bb4dcc7dbc710585d0b8d03
90	2026-08-19 15:43:34	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-11"}	2d26db42f6c80dbb218324dcf206b9f2250489ef3bb4dcc7dbc710585d0b8d03	0eded40c8ed4595faf8eefe78a8c2ea622939fdbebd372b5ead85510962d385f
91	2026-08-19 15:43:34	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	0eded40c8ed4595faf8eefe78a8c2ea622939fdbebd372b5ead85510962d385f	4d23317844e42e6ad189d95b1a6a60d762eb94cab79af79846eacd7d494da82e
92	2026-08-19 15:43:34	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	4d23317844e42e6ad189d95b1a6a60d762eb94cab79af79846eacd7d494da82e	ef5c7a4569be412f0a422da08dbef87baf1b572e25ac5d0706609cd8cc77c65b
93	2026-08-19 15:43:39	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:43:39.766816"}	ef5c7a4569be412f0a422da08dbef87baf1b572e25ac5d0706609cd8cc77c65b	ce104a5442140b289fd4c78afd0838e0eb6feb4fcd539b44c5bb97376642cf45
94	2026-08-19 15:43:39	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	ce104a5442140b289fd4c78afd0838e0eb6feb4fcd539b44c5bb97376642cf45	e57a3d90ee6e53c6bf699abb37e0b49e171311e74d0d029ad1ab52899508a8d8
95	2026-08-19 15:43:42	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:43:42.815467"}	e57a3d90ee6e53c6bf699abb37e0b49e171311e74d0d029ad1ab52899508a8d8	a4764c1b143aa42aec6607b4cbaab98a5cf823a4ac2604315ba89ec084a540ed
96	2026-08-19 15:43:42	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	a4764c1b143aa42aec6607b4cbaab98a5cf823a4ac2604315ba89ec084a540ed	206b82c5d9b6b73e058e5ceb3e0738f03001791df45b88995cf6381b618016aa
97	2026-08-19 15:43:47	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:43:47.001162"}	206b82c5d9b6b73e058e5ceb3e0738f03001791df45b88995cf6381b618016aa	f8775d8ec72ba01f96899ee521ef71b93313302dd2d9125c0cdd73ea93baaf6d
98	2026-08-19 15:43:47	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	f8775d8ec72ba01f96899ee521ef71b93313302dd2d9125c0cdd73ea93baaf6d	d390f77711b2a6f756a3433a4e147c2fa33d5f71375f2e8b188d674c9868adb9
99	2026-08-19 15:44:20	user_login	{"username": "test_viewer", "role": "viewer", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:44:20.697715"}	d390f77711b2a6f756a3433a4e147c2fa33d5f71375f2e8b188d674c9868adb9	f7ea4ef15615f6ea6143e85549ee9ad3c92b96b57c56ef3bc58b8b30ebfb9760
100	2026-08-19 15:44:20	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "4", "source_entity_type": "USER", "recipients_count": 3}	f7ea4ef15615f6ea6143e85549ee9ad3c92b96b57c56ef3bc58b8b30ebfb9760	dc67e63e2f692a04b2216dca0e3733877821f04ecd828cd89d8abb2a3c34c30a
101	2026-08-19 15:44:24	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:44:24.181223"}	dc67e63e2f692a04b2216dca0e3733877821f04ecd828cd89d8abb2a3c34c30a	e13c4eca6249c063035659f35117be79d174dc0dcdbeb6e39810fa00cc6c124a
102	2026-08-19 15:44:24	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	e13c4eca6249c063035659f35117be79d174dc0dcdbeb6e39810fa00cc6c124a	7c1b91b21c4d6dad73312014fe103a64c064f3ac3e5dc31b2af8ee357e8d1a70
103	2026-08-19 15:45:00	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:45:00.764835"}	7c1b91b21c4d6dad73312014fe103a64c064f3ac3e5dc31b2af8ee357e8d1a70	0df4b3ed0f356d64ff83a5c6079e1538a0b23ece2752aca11df9119ae9e50f42
104	2026-08-19 15:45:01	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	0df4b3ed0f356d64ff83a5c6079e1538a0b23ece2752aca11df9119ae9e50f42	f9c4ab9ea6adcd54b5a8e9487c069594d2a143bb87c50d30124c722eac06e03f
105	2026-08-19 15:45:11	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:45:11.724794"}	f9c4ab9ea6adcd54b5a8e9487c069594d2a143bb87c50d30124c722eac06e03f	88c41f9984f7745389dfdf77773e12e8b481b236f94fdec380d791637b2d04ba
106	2026-08-19 15:45:11	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	88c41f9984f7745389dfdf77773e12e8b481b236f94fdec380d791637b2d04ba	ae0e3cf1a43e4154ee31f0318f7ba0bd530b1206a69e656765437da86206a64c
107	2026-08-19 15:56:33	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	ae0e3cf1a43e4154ee31f0318f7ba0bd530b1206a69e656765437da86206a64c	cfd3b0730a9f381cdfcaf81e28567978bdc57a35167ea8257a0c8ec8bfd9a2a4
108	2026-08-19 15:56:33	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	cfd3b0730a9f381cdfcaf81e28567978bdc57a35167ea8257a0c8ec8bfd9a2a4	4621c68cf4fb88d29e71bf9da68222f8531cbccc3262abe0bd28e8ba70d3f093
109	2026-08-19 15:56:33	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	4621c68cf4fb88d29e71bf9da68222f8531cbccc3262abe0bd28e8ba70d3f093	ce6def05fd3a77c38097e8afdd94c1d5dda6b75482238cebabf05f1988f69556
110	2026-08-19 15:56:33	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	ce6def05fd3a77c38097e8afdd94c1d5dda6b75482238cebabf05f1988f69556	3b6a55072b9eb5a63b8bf574ac460e41a9559a96b9998ca93803705280dee4b7
111	2026-08-19 15:56:33	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	3b6a55072b9eb5a63b8bf574ac460e41a9559a96b9998ca93803705280dee4b7	7086d2e3e6a8e45319c880050c53aa79315cab559d014abea52e1ae9cf433ad1
113	2026-08-19 15:56:33	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	ab875242ff043ca3ff87cbc285e0f669a4f218a220451b30a3fa22969f36c8e3	9a8d47bfd940fbbe6ccc5f1f78a8d43b327ab7c68ac3a7834cb7caab71e70bb0
114	2026-08-19 15:56:33	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	9a8d47bfd940fbbe6ccc5f1f78a8d43b327ab7c68ac3a7834cb7caab71e70bb0	da3b2f1487adde0b80010c55ba2084476496283c3509594a878ec3d1560dee3e
115	2026-08-19 15:56:33	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	da3b2f1487adde0b80010c55ba2084476496283c3509594a878ec3d1560dee3e	f22a844d1cbc02ad1f0a758b126f5e7d2f348c6ae540fcc04e30de2dff5d62b4
116	2026-08-19 15:56:33	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	f22a844d1cbc02ad1f0a758b126f5e7d2f348c6ae540fcc04e30de2dff5d62b4	65bf0807ab1814252bdeca934be5c3436987640c2c437e0bf500b31b6f5c28f2
117	2026-08-19 15:56:33	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	65bf0807ab1814252bdeca934be5c3436987640c2c437e0bf500b31b6f5c28f2	1d0423ef5e4810d29ab783de51a30e5fffd618adb26f120f9a14fe0068bf8dd4
118	2026-08-19 15:56:33	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	1d0423ef5e4810d29ab783de51a30e5fffd618adb26f120f9a14fe0068bf8dd4	313728c95e79949e1b850d4270f6ec511c3f11f5077e0cf1f91334b8496dccb5
119	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	313728c95e79949e1b850d4270f6ec511c3f11f5077e0cf1f91334b8496dccb5	bff8f1e0f1eccf7d8c19fec2ef1cb4c715a65eb93dadc1db6eb40b612005325e
120	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	bff8f1e0f1eccf7d8c19fec2ef1cb4c715a65eb93dadc1db6eb40b612005325e	effa04d94df62b817cac95b3f139dcc1925dc115313ded9f1f248e4b10507897
121	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	effa04d94df62b817cac95b3f139dcc1925dc115313ded9f1f248e4b10507897	d37d7bdf3d9148318c492ec3e1e25d75a36e04ad82ab90bad59e8e2831d9f381
122	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	d37d7bdf3d9148318c492ec3e1e25d75a36e04ad82ab90bad59e8e2831d9f381	a5bee70c94e8ed01718cec39da20ec4e692c6f6843cd24a927b5e9234c06c998
123	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	a5bee70c94e8ed01718cec39da20ec4e692c6f6843cd24a927b5e9234c06c998	80c03968be1e4b75ecb769af7074a3f7b68f60ce66971780869ed98c79697d71
124	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	80c03968be1e4b75ecb769af7074a3f7b68f60ce66971780869ed98c79697d71	2d63eeaa42af863260ae7c0d9ce3ebeddcd37805acb0bc9c6f41259ac6c7c492
125	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	2d63eeaa42af863260ae7c0d9ce3ebeddcd37805acb0bc9c6f41259ac6c7c492	bac832e19f9174bb165adb6f04fba1742230d6c97a06249482983f5b751569b5
126	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	bac832e19f9174bb165adb6f04fba1742230d6c97a06249482983f5b751569b5	38a1fa050b997088e4880c0418193e1262dfbd617a79144b656943593f1b91f8
127	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	38a1fa050b997088e4880c0418193e1262dfbd617a79144b656943593f1b91f8	879a272973c805534656e8da9670bfe8b00605e79b1cb3f86e4c356515ca0530
128	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	879a272973c805534656e8da9670bfe8b00605e79b1cb3f86e4c356515ca0530	670fe2f6a205d808ae19ac2028da3947657322053dc2f70e0853883a90529d9b
129	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	670fe2f6a205d808ae19ac2028da3947657322053dc2f70e0853883a90529d9b	f88207abfca2c537d5a50660836927750556ae3c2e1d4df8b18d2f9e51c76ccd
130	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-01"}	f88207abfca2c537d5a50660836927750556ae3c2e1d4df8b18d2f9e51c76ccd	76cf25b5ad3bac1978b195f128501806a1a35f63ef0d1b65a08edc6b66abf7c2
131	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	76cf25b5ad3bac1978b195f128501806a1a35f63ef0d1b65a08edc6b66abf7c2	6f95fb98241a9176d48f5e8023cbfffe4e2e273f54277955f5a35396085bad00
132	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	6f95fb98241a9176d48f5e8023cbfffe4e2e273f54277955f5a35396085bad00	4bfbbdd3896d84af78843a445bf131e1050649805478fa9faf2f48360889f82a
133	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-02"}	4bfbbdd3896d84af78843a445bf131e1050649805478fa9faf2f48360889f82a	2c5295b60317d91236801ced47a58cf07071ff876afd0e419696095fcb7e298e
134	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	2c5295b60317d91236801ced47a58cf07071ff876afd0e419696095fcb7e298e	5a65ae7dfabffce2a7d998b3fef0780d6a4bf8de5c385ae75ca55f93daad4e82
135	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-03"}	5a65ae7dfabffce2a7d998b3fef0780d6a4bf8de5c385ae75ca55f93daad4e82	a51677366da3eb083ac0e971c44b258e7c8b67e5cf960127aa3c8790a78558a4
136	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	a51677366da3eb083ac0e971c44b258e7c8b67e5cf960127aa3c8790a78558a4	345dddb32f6d3a5b7f2b2d947999cb0b10c0e54e1d402234433839d8b657401e
137	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-03"}	345dddb32f6d3a5b7f2b2d947999cb0b10c0e54e1d402234433839d8b657401e	3dda2c33abeec76022a09d155f0d283cad2691456bee61c786fac71dec59eb4d
138	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-03"}	3dda2c33abeec76022a09d155f0d283cad2691456bee61c786fac71dec59eb4d	de65e5ede4698984a7da3f67cc0b0661dd61e87218709ef5cbbe41a61d15e00f
139	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	de65e5ede4698984a7da3f67cc0b0661dd61e87218709ef5cbbe41a61d15e00f	481e5c4aa3839528e27f842359da236e7baf2fce8a659c09911106840e40c16c
140	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	481e5c4aa3839528e27f842359da236e7baf2fce8a659c09911106840e40c16c	3348d7723bb02c80e72fc95b9cad8fe3a2fe6b6677d48d2a3981d6503e73bac3
344	2026-08-19 18:16:08.757556	EXPERIMENT_CREATED	{"experiment_id": 1, "name": "OR-Tools Priority Test", "created_by": "admin"}	SYSTEM	SYSTEM
141	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-04"}	3348d7723bb02c80e72fc95b9cad8fe3a2fe6b6677d48d2a3981d6503e73bac3	016d85ef34054ebad9971ea9fbb2e49d59e9d83640539c302843599137d9d5ba
142	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	016d85ef34054ebad9971ea9fbb2e49d59e9d83640539c302843599137d9d5ba	196b4e45eada7693cf7a707a09ffd8864e0217594af652b0276402a9f1ebb484
143	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-06"}	196b4e45eada7693cf7a707a09ffd8864e0217594af652b0276402a9f1ebb484	f3b34142266fc6219848a87e052bc93d0e64dabc1b91e76804bbe06df1859949
144	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-08"}	f3b34142266fc6219848a87e052bc93d0e64dabc1b91e76804bbe06df1859949	4247563b53cdd288bdaf6e4f59ff2579e76e8e3434528221bce5907687123384
145	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-SSD-01", "quantity": 90, "date": "2026-08-09"}	4247563b53cdd288bdaf6e4f59ff2579e76e8e3434528221bce5907687123384	d1cd9e2930b2cfd1e6e6aff81f1aacaa5bce86fbc1bd9525b4033a5594583ef1
146	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-09"}	d1cd9e2930b2cfd1e6e6aff81f1aacaa5bce86fbc1bd9525b4033a5594583ef1	0ec7aa82fa1cb0b60cbf74c739797099c9fc440d912855df8dfb4464d35efb9a
147	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-10"}	0ec7aa82fa1cb0b60cbf74c739797099c9fc440d912855df8dfb4464d35efb9a	621f70c3354896b065373f5fea57ffa5c811f017e8829c9389aaf7202275b9bd
148	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	621f70c3354896b065373f5fea57ffa5c811f017e8829c9389aaf7202275b9bd	505623687f6fbef1f49418e314145154eff48a08336dc57d8e96f45281b51454
149	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	505623687f6fbef1f49418e314145154eff48a08336dc57d8e96f45281b51454	ab2060da46bde08709e10344dd7dc1e7b537ecb0508ad649386a5c67e2e4c710
150	2026-08-19 15:56:33	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	ab2060da46bde08709e10344dd7dc1e7b537ecb0508ad649386a5c67e2e4c710	359649b45d9bf0c63a50bae8c12c754d2ff6733d995e6d426027e41e4ea94dfb
151	2026-08-19 15:56:33	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	359649b45d9bf0c63a50bae8c12c754d2ff6733d995e6d426027e41e4ea94dfb	efe3bd06654aed438c22014787fdc156c25a8330ee71dd29819cffe811415dce
152	2026-08-19 15:56:33	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	efe3bd06654aed438c22014787fdc156c25a8330ee71dd29819cffe811415dce	083b4204f5c6ce075c17c426c33f5c7da2c1d796aae0edd4b7fcb5d69fca2754
153	2026-08-19 15:56:47	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T15:56:47.542665"}	083b4204f5c6ce075c17c426c33f5c7da2c1d796aae0edd4b7fcb5d69fca2754	aaa4e2dcfcb29d3ddf6fb8601fa8cb1e732633003e741762a0ad2d79878c71ef
154	2026-08-19 15:56:47	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	aaa4e2dcfcb29d3ddf6fb8601fa8cb1e732633003e741762a0ad2d79878c71ef	f2086c407432a4ef70e533b7caee566f72f4af4b3dcf16f2123fd2eec4699573
155	2026-08-19 16:12:43	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	f2086c407432a4ef70e533b7caee566f72f4af4b3dcf16f2123fd2eec4699573	79978821620c3d17138880badfd547ad8de6cd61d854522fd664b8288d1bf060
156	2026-08-19 16:12:43	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	79978821620c3d17138880badfd547ad8de6cd61d854522fd664b8288d1bf060	fc0558f5628e892c0f2aa9cfd718e6f6187a716047ed32bc9f9436bced7c7311
157	2026-08-19 16:12:43	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	fc0558f5628e892c0f2aa9cfd718e6f6187a716047ed32bc9f9436bced7c7311	ec2a47e69357318433e030c2f54d587a54b3db233c0580df5fde197d276b8f95
158	2026-08-19 16:12:43	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	ec2a47e69357318433e030c2f54d587a54b3db233c0580df5fde197d276b8f95	d5fcd5eb272cede56c2085cbb86a0d7a43fad49cc8c3d28ac8314f2933cf21d1
159	2026-08-19 16:12:43	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	d5fcd5eb272cede56c2085cbb86a0d7a43fad49cc8c3d28ac8314f2933cf21d1	5c2b6f73977c74753bf11ae7a83178177cdffcc903dbad8f8cb0c1e7e4eebc35
160	2026-08-19 16:12:43	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	5c2b6f73977c74753bf11ae7a83178177cdffcc903dbad8f8cb0c1e7e4eebc35	2209ca62419caed5f193960c0e06c5ea8ad2919134f45bde4636c80d84c4cd73
161	2026-08-19 16:12:43	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	2209ca62419caed5f193960c0e06c5ea8ad2919134f45bde4636c80d84c4cd73	37b3c144e13c1321973dc114ed3677e17eed58f3bdf77298bbc38101c40ec736
162	2026-08-19 16:12:43	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	37b3c144e13c1321973dc114ed3677e17eed58f3bdf77298bbc38101c40ec736	46c20c23f8af2017dc516e437615f7f72e293c8f6ead8570f5fbd697aa1bde36
163	2026-08-19 16:12:43	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	46c20c23f8af2017dc516e437615f7f72e293c8f6ead8570f5fbd697aa1bde36	0f37cdff1957c0c83f8b0b61640f2d0ff7c6d80f5a59df0c1cddb2dbd450a543
164	2026-08-19 16:12:43	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	0f37cdff1957c0c83f8b0b61640f2d0ff7c6d80f5a59df0c1cddb2dbd450a543	9ba3d8d902c1819d05333e918bedfa09e81013410a67b5de23f1e55d6556940b
165	2026-08-19 16:12:43	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	9ba3d8d902c1819d05333e918bedfa09e81013410a67b5de23f1e55d6556940b	cc57de1e859b4d04aa7cf53a7eadb67887a8cfee42cc281330b81e89573255f7
166	2026-08-19 16:12:43	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	cc57de1e859b4d04aa7cf53a7eadb67887a8cfee42cc281330b81e89573255f7	42f3b871f40118456fad2a13b1a53422ce0bdfb387222cb97bd9529a9c68e55c
167	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-18"}	42f3b871f40118456fad2a13b1a53422ce0bdfb387222cb97bd9529a9c68e55c	b2d35ecac5d171ce2e3e473eee4aa15aa166eceee9c7f79cbf003044a1bc8c84
168	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	b2d35ecac5d171ce2e3e473eee4aa15aa166eceee9c7f79cbf003044a1bc8c84	577909e4491728cdc729bee16c4af62f8ab602cd162eb4b12ac3f8c6a8bff315
169	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	577909e4491728cdc729bee16c4af62f8ab602cd162eb4b12ac3f8c6a8bff315	3422ae8d73d96d1502edb895604c54756a7998cd760972a6e37c1238e1e6fd00
170	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-22"}	3422ae8d73d96d1502edb895604c54756a7998cd760972a6e37c1238e1e6fd00	81f4d5e2d82e49a10f3a3aee2caf69c3e77b03ad77d7e15d24ccc593a2fb9064
171	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-23"}	81f4d5e2d82e49a10f3a3aee2caf69c3e77b03ad77d7e15d24ccc593a2fb9064	a82a13e8b812c04f35d6862fff7d56745eed39ad7a7ba79d4b371d20159eefd0
172	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	a82a13e8b812c04f35d6862fff7d56745eed39ad7a7ba79d4b371d20159eefd0	86d88a0bef8074c843da9016593eb2c67f875726a1bab9f118e71ce1dd199eff
173	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	86d88a0bef8074c843da9016593eb2c67f875726a1bab9f118e71ce1dd199eff	07eb50e761b8317c08e412a9baaac0e51948a0ecbef6d61419ea82e0d9b333e1
174	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	07eb50e761b8317c08e412a9baaac0e51948a0ecbef6d61419ea82e0d9b333e1	8455394ebff82328ab58f77dc4e7977ae9879a5ccc6583cc46187f28644fe646
175	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	8455394ebff82328ab58f77dc4e7977ae9879a5ccc6583cc46187f28644fe646	3ab05a28ad4e978600536a0254416a4f5d9cf8429abb35ffc92340d1d4bf5e2f
176	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	3ab05a28ad4e978600536a0254416a4f5d9cf8429abb35ffc92340d1d4bf5e2f	59a972bce3b48ecaffb39f8a971fd3de3921fc42695c35fd61b327de8c424e85
177	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-29"}	59a972bce3b48ecaffb39f8a971fd3de3921fc42695c35fd61b327de8c424e85	866c9382397c49cab3336f28397ff0881ddc759368b9ed8603b4fb47928959b2
178	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-07-30"}	866c9382397c49cab3336f28397ff0881ddc759368b9ed8603b4fb47928959b2	5177bb0d44916ee511fcb07189eea41c75f442bf0ffb56ceaade1cfbed11b189
179	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-01"}	5177bb0d44916ee511fcb07189eea41c75f442bf0ffb56ceaade1cfbed11b189	61cf8aabd2ba4db21238e7816e014394192739fdf9859311b8287591b5232e96
180	2026-08-19 16:12:43	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-08-01"}	61cf8aabd2ba4db21238e7816e014394192739fdf9859311b8287591b5232e96	6e206d2e8614e14760478cf7ce887a8932a90f77d1e721ea957950099d3efc07
181	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	6e206d2e8614e14760478cf7ce887a8932a90f77d1e721ea957950099d3efc07	088671ef22b3ad2d903ed83ce97b51d0ef21dbf0bf0ae19160a5c7d8b8472245
182	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-02"}	088671ef22b3ad2d903ed83ce97b51d0ef21dbf0bf0ae19160a5c7d8b8472245	04e1b4c0275613c33fa5e1ecffc66dda2f845208ce67e82fd4cac6c163ff285e
183	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	04e1b4c0275613c33fa5e1ecffc66dda2f845208ce67e82fd4cac6c163ff285e	7154fb254606042243eacf34b87bdb92124f20eb671080f858db442d3a87b408
184	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	7154fb254606042243eacf34b87bdb92124f20eb671080f858db442d3a87b408	fc3c86f2ef29fc2213a5819d157df928dbef4593478c50fc7394269a1b12e5f8
185	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	fc3c86f2ef29fc2213a5819d157df928dbef4593478c50fc7394269a1b12e5f8	99ce48f6fc8c2790d525a53b99e113ce49f0fe9ea22f0bf92bd7366fc38385b5
186	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	99ce48f6fc8c2790d525a53b99e113ce49f0fe9ea22f0bf92bd7366fc38385b5	9c2735c1d36e269df9638ce28d296e2acd623e8caf08e076d50203165b7bb9d9
187	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-06"}	9c2735c1d36e269df9638ce28d296e2acd623e8caf08e076d50203165b7bb9d9	158a9a6b6529cae1dbfbbf3bbc7ecfc4558910a5f54351825c3a131887769457
188	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-06"}	158a9a6b6529cae1dbfbbf3bbc7ecfc4558910a5f54351825c3a131887769457	75284fc60e0fd897a9be1cfa254f86445fd8aef6f874c3e6a3d3b7358fefb46e
189	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-07"}	75284fc60e0fd897a9be1cfa254f86445fd8aef6f874c3e6a3d3b7358fefb46e	c3562a8c17d3cef66a4f4bdebfdc7f95898f790dd530c68e6bbf0fb83034e96b
190	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-07"}	c3562a8c17d3cef66a4f4bdebfdc7f95898f790dd530c68e6bbf0fb83034e96b	b8c94934f0510ac7fd13671f29d28395b45b8bf60e8219ec793d534e8efcea3d
191	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-09"}	b8c94934f0510ac7fd13671f29d28395b45b8bf60e8219ec793d534e8efcea3d	c3986f12bbf560ac476c64035405be7dc574016ba2521a9f1347708c0e0ff7a3
192	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-09"}	c3986f12bbf560ac476c64035405be7dc574016ba2521a9f1347708c0e0ff7a3	9c4d1dc095d6058007bf877a96e93958ac9c5aaf895be243099a76cf47b0f77d
193	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-09"}	9c4d1dc095d6058007bf877a96e93958ac9c5aaf895be243099a76cf47b0f77d	c10fc5a254db7a1ed0e781e4b070767e92da5c8914a099eef1acd9608c789b50
194	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-09"}	c10fc5a254db7a1ed0e781e4b070767e92da5c8914a099eef1acd9608c789b50	ecd2e2b86547acd0048d50a3a7ef2074a7cd792a5b4229167eba08311a8514d9
195	2026-08-19 16:12:44	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-11"}	ecd2e2b86547acd0048d50a3a7ef2074a7cd792a5b4229167eba08311a8514d9	81cc75b019be414bf0979e37b9c2ec90b81ae06179820a2b968dcb02f83fb06b
196	2026-08-19 16:12:44	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	81cc75b019be414bf0979e37b9c2ec90b81ae06179820a2b968dcb02f83fb06b	6fa1e1ae5e2966b1f9a0a41dc68017e0b150912c855b4084169cd2e0cfcf4d5c
197	2026-08-19 16:12:44	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	6fa1e1ae5e2966b1f9a0a41dc68017e0b150912c855b4084169cd2e0cfcf4d5c	a920153fb26062534a66b5dd73f269b594f37ed657f55e18a74d7f5a3403d1a5
198	2026-08-19 16:13:00	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:13:00.687456"}	a920153fb26062534a66b5dd73f269b594f37ed657f55e18a74d7f5a3403d1a5	98da5ff963092b51a7e629f6b45239ce1f784cbbe5586c90805815b62a8af403
199	2026-08-19 16:13:00	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	98da5ff963092b51a7e629f6b45239ce1f784cbbe5586c90805815b62a8af403	0ad05845190995a7f35e87500db665eb3d71119211b790e37bfd7a0dbb4bbc45
200	2026-08-19 16:13:20	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:13:20.247682"}	0ad05845190995a7f35e87500db665eb3d71119211b790e37bfd7a0dbb4bbc45	663b14322d911300eeab42602e7d5e82268b7b72e75d3049fd316959634f7719
201	2026-08-19 16:13:20	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	663b14322d911300eeab42602e7d5e82268b7b72e75d3049fd316959634f7719	73f1623c27e979cc525025ec1aac7dc4298428bad688a70439f784d4de4603d9
202	2026-08-19 16:13:22	AI_ASSISTANT_QUERY	{"user": "admin", "query": "Show me the robot fleet status", "warehouse_id": "WH-BLR-01"}	73f1623c27e979cc525025ec1aac7dc4298428bad688a70439f784d4de4603d9	79cb6da566608f7ca0ca7a1cbf2a582b7b16bfc2b5b6ba9ba5dd74d4570305e9
203	2026-08-19 16:13:25	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:13:25.682049"}	79cb6da566608f7ca0ca7a1cbf2a582b7b16bfc2b5b6ba9ba5dd74d4570305e9	c90d2b30b8a80d6278ddaa341b9d2343d726e161186aa1d4222e0ae548848306
204	2026-08-19 16:13:25	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	c90d2b30b8a80d6278ddaa341b9d2343d726e161186aa1d4222e0ae548848306	504f2173c1e26b42f224bad3d711844ee273abc8409bc8e552371deef6d6283b
205	2026-08-19 16:19:14	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	504f2173c1e26b42f224bad3d711844ee273abc8409bc8e552371deef6d6283b	aff966387bd03162359f29293e99dc15a7133b6426adaf79317a1b93610a77df
206	2026-08-19 16:19:14	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	aff966387bd03162359f29293e99dc15a7133b6426adaf79317a1b93610a77df	257c9f61c11626411d10ac11de53cbd9dea68d5f0c9c310941b1d938294ebb42
207	2026-08-19 16:19:14	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	257c9f61c11626411d10ac11de53cbd9dea68d5f0c9c310941b1d938294ebb42	ede4ddafa1c074e8b262d7876d4ca08bca6befc49ee0d7590365ffe41c7013d3
208	2026-08-19 16:19:14	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	ede4ddafa1c074e8b262d7876d4ca08bca6befc49ee0d7590365ffe41c7013d3	5f6cc4f0f603dfb1425d26c56bcd77b46faea8825963a2c42b44822b9f58d605
209	2026-08-19 16:19:14	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	5f6cc4f0f603dfb1425d26c56bcd77b46faea8825963a2c42b44822b9f58d605	5c9db8732d5cdbb8d33e04d30d1a9b6af7268347b2b3816c22280489b6539a9e
210	2026-08-19 16:19:14	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	5c9db8732d5cdbb8d33e04d30d1a9b6af7268347b2b3816c22280489b6539a9e	ada7450bbbdc7e11bc4035877c8d72ab8a6f0b9f76023239e54100f2187a413e
211	2026-08-19 16:19:14	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	ada7450bbbdc7e11bc4035877c8d72ab8a6f0b9f76023239e54100f2187a413e	5259bbe8d6bd48f0e833e79418bc71a358e8bc50ce4cacfb3efae9b3d4a83343
212	2026-08-19 16:19:14	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	5259bbe8d6bd48f0e833e79418bc71a358e8bc50ce4cacfb3efae9b3d4a83343	dec95f1c1db856d687d2f1a1e31cac2ea64a0cc5596b4eafb4d7534e303e2455
213	2026-08-19 16:19:14	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	dec95f1c1db856d687d2f1a1e31cac2ea64a0cc5596b4eafb4d7534e303e2455	b16a7f7788f49b366fb0f0a619252472e08945e228c0f7508e1e0d97ce10d92f
214	2026-08-19 16:19:14	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	b16a7f7788f49b366fb0f0a619252472e08945e228c0f7508e1e0d97ce10d92f	ca6d45c34ccad3e6dea257496bc3abb4649a567889b3170930de8f8d3c79bc21
215	2026-08-19 16:19:14	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	ca6d45c34ccad3e6dea257496bc3abb4649a567889b3170930de8f8d3c79bc21	6a2bcabdf0f5520d3ea3f889108d46f1d39e4b4b1c178bf0536924a4820b4427
216	2026-08-19 16:19:14	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	6a2bcabdf0f5520d3ea3f889108d46f1d39e4b4b1c178bf0536924a4820b4427	efbadc519ddf58312c48868acd94017e308cc6df876d6382321014de31af1e48
217	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	efbadc519ddf58312c48868acd94017e308cc6df876d6382321014de31af1e48	74c43f8e4b7352f913a5b74fe7484684ce02ffb98f5c8a752966190cf8290596
218	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	74c43f8e4b7352f913a5b74fe7484684ce02ffb98f5c8a752966190cf8290596	2ffa769c27fb93b979db18f585faad3bfb822433e53b07b9937b78fd1ca4417a
219	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	2ffa769c27fb93b979db18f585faad3bfb822433e53b07b9937b78fd1ca4417a	04f02717f82f39c3feeeac769c164b0af6d7377b948ae196534dce96c2b157be
220	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	04f02717f82f39c3feeeac769c164b0af6d7377b948ae196534dce96c2b157be	f40d97018ec827b8d762b0e32e180f80d302a3de42a52b09093553364d91fe71
221	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	f40d97018ec827b8d762b0e32e180f80d302a3de42a52b09093553364d91fe71	c0f1fdcc57d95f20fd1f0ef692775be77e41b2d3fd5f249a0d21a15ef6cdad96
222	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-25"}	c0f1fdcc57d95f20fd1f0ef692775be77e41b2d3fd5f249a0d21a15ef6cdad96	ef76787abac39b885ba5d6633148e1aa378bfb900abfc5c107ba42cad79233fd
223	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	ef76787abac39b885ba5d6633148e1aa378bfb900abfc5c107ba42cad79233fd	e6a4574aa44dca9584f67b7ae7ba857db98b9ebdc89251f53c6199fb12efc147
224	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	e6a4574aa44dca9584f67b7ae7ba857db98b9ebdc89251f53c6199fb12efc147	7fb9cd23ddb8d47d187250446c8fd7f614098e5525c28207c4b09143cd71946f
225	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	7fb9cd23ddb8d47d187250446c8fd7f614098e5525c28207c4b09143cd71946f	0787272305e0dc97468ed91b4e9eacee05dd0a2bae9b6e67f40fde50e9659b00
226	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	0787272305e0dc97468ed91b4e9eacee05dd0a2bae9b6e67f40fde50e9659b00	b103bb87ae05dce13899ec8ef56c210d162a34b4b7b5fbe95f99eaec1d002e7c
227	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	b103bb87ae05dce13899ec8ef56c210d162a34b4b7b5fbe95f99eaec1d002e7c	89d424d99c01f499e7123b4f0d28fc980c91ddcb70d291ddea4f6a658783991b
228	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-31"}	89d424d99c01f499e7123b4f0d28fc980c91ddcb70d291ddea4f6a658783991b	726264fe1ebe96e3e35d2842120219e3b5b8c1dcdbbd65d0fe60b19d810b1f47
229	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-07-31"}	726264fe1ebe96e3e35d2842120219e3b5b8c1dcdbbd65d0fe60b19d810b1f47	34352b6022c5aa5048460bdbdf6c19c52561cb7c4bddfcc2173c81af7c0665a7
230	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-31"}	34352b6022c5aa5048460bdbdf6c19c52561cb7c4bddfcc2173c81af7c0665a7	dd7eb3d94be516cd8acf8f2bd7a0a72e21271fff4720c4b833956df6f99f0c32
231	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	dd7eb3d94be516cd8acf8f2bd7a0a72e21271fff4720c4b833956df6f99f0c32	b18957fe680d95b599b1994ac84dbf1577301c5791bdb047b7f996f17c485b83
232	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-01"}	b18957fe680d95b599b1994ac84dbf1577301c5791bdb047b7f996f17c485b83	0ff5432cd7a7b3568d8657f0be71baaafc248c9986929d75249997695ffa2774
233	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-01"}	0ff5432cd7a7b3568d8657f0be71baaafc248c9986929d75249997695ffa2774	fce338859d8857624202460131899265b0993b41fdccf07bedac0c1c77ef674f
234	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-02"}	fce338859d8857624202460131899265b0993b41fdccf07bedac0c1c77ef674f	e947f07b132ee8aac61930a847a802fb9e3a651b273a66f93d3ce06643eb20ef
235	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	e947f07b132ee8aac61930a847a802fb9e3a651b273a66f93d3ce06643eb20ef	0e176c0f87d49e21a607a26b5bdd6bf82d641c794d116d72be77084cc07fd561
236	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	0e176c0f87d49e21a607a26b5bdd6bf82d641c794d116d72be77084cc07fd561	2a1303756141add076c081ed2eabe228abfa7a01fa352e33002daa73ea7f13d0
237	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-04"}	2a1303756141add076c081ed2eabe228abfa7a01fa352e33002daa73ea7f13d0	067dd0f07c37a5a3df145d803d7dfd0c55bcd67c73b05b288f3cd90382661be1
238	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	067dd0f07c37a5a3df145d803d7dfd0c55bcd67c73b05b288f3cd90382661be1	b25df998f1966349da893739f529bc56a85d1a895271584f0597fb17c43dd0c7
239	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-05"}	b25df998f1966349da893739f529bc56a85d1a895271584f0597fb17c43dd0c7	312a6b0749f7a470845220ee93dcb09c0c3b98e6e83c899b3ee6c5969e66b2a3
240	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	312a6b0749f7a470845220ee93dcb09c0c3b98e6e83c899b3ee6c5969e66b2a3	9374adca0a990c3fbf3b75f0060f85fcdfd529227196aa103c9cdb191a4718c1
241	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-06"}	9374adca0a990c3fbf3b75f0060f85fcdfd529227196aa103c9cdb191a4718c1	008a27b08edbf88f85ee1878e548e4ee629c36e185213426d2e5e20e2b44617f
242	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-06"}	008a27b08edbf88f85ee1878e548e4ee629c36e185213426d2e5e20e2b44617f	622ad24cb3b19c20fc3707fc2dfa6046d80f21c3c6f6cb5c3a64cf4a1639c7ff
243	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-07"}	622ad24cb3b19c20fc3707fc2dfa6046d80f21c3c6f6cb5c3a64cf4a1639c7ff	d8c1d434fd3b36aebc7b3412fff17333c7d45cfce94009dbbc53628aec907a7b
244	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-08"}	d8c1d434fd3b36aebc7b3412fff17333c7d45cfce94009dbbc53628aec907a7b	1b95812f1a4593dc33f602fbdb7ffc859f11ce2aded95a4c20814bcb1ed48b97
245	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-08"}	1b95812f1a4593dc33f602fbdb7ffc859f11ce2aded95a4c20814bcb1ed48b97	ae3b5d8cffbd5e1027cf6054db346fb86f1be4bf3a510456b63bbb93bf802ff9
246	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-09"}	ae3b5d8cffbd5e1027cf6054db346fb86f1be4bf3a510456b63bbb93bf802ff9	2edea224c7ada2227200a0d879e86ef713c7d6cdfd238d80ab6980f3f9958a32
247	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-09"}	2edea224c7ada2227200a0d879e86ef713c7d6cdfd238d80ab6980f3f9958a32	2193f316a1554c05e38d29d416a2bdc11de541dfd8adbbcd8579a63559d2b5a3
248	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-10"}	2193f316a1554c05e38d29d416a2bdc11de541dfd8adbbcd8579a63559d2b5a3	ddaf534a07c17c909a1415748bf3b78fa09221f3aba1d9a6dc9cda626bf35167
249	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	ddaf534a07c17c909a1415748bf3b78fa09221f3aba1d9a6dc9cda626bf35167	3b54c5f2d50d7eab0e486edd31303fa14bc8069d39315e6a5803111485ba481c
250	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	3b54c5f2d50d7eab0e486edd31303fa14bc8069d39315e6a5803111485ba481c	ed1c5b06d5ecc838b5402de05ba25bb940cbdce81cabe919d4d3b224734f14aa
251	2026-08-19 16:19:14	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	ed1c5b06d5ecc838b5402de05ba25bb940cbdce81cabe919d4d3b224734f14aa	aa6e20a7df0cf1f140b62d6556127aba2c29042ce3db3dc0fd894fc0efa17dce
252	2026-08-19 16:19:14	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	aa6e20a7df0cf1f140b62d6556127aba2c29042ce3db3dc0fd894fc0efa17dce	fb04d52fbd5463645e9e1b19672df2496a20d04bbc73ce371fbbe95e1a0f57b6
253	2026-08-19 16:19:14	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	fb04d52fbd5463645e9e1b19672df2496a20d04bbc73ce371fbbe95e1a0f57b6	a41b458ccb1066c95bfe2cefb10318140de19716bbda4be3c09b743a682a194b
254	2026-08-19 16:19:21	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:19:21.708926"}	a41b458ccb1066c95bfe2cefb10318140de19716bbda4be3c09b743a682a194b	9f0dffbd1e5107de933f3de892d54a9bdbb7f64fc4e145be41714812e04610e1
255	2026-08-19 16:19:21	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	9f0dffbd1e5107de933f3de892d54a9bdbb7f64fc4e145be41714812e04610e1	390bbafb2fcc64e83941c70e47e8cb932d112a6473dc66626a14a31afee23e52
256	2026-08-19 16:27:27	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:27:27.161865"}	390bbafb2fcc64e83941c70e47e8cb932d112a6473dc66626a14a31afee23e52	1d16e67a8b62f8eed35692737c451c0396945f45931e7a7748f5c4e1614518cf
257	2026-08-19 16:27:27	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	1d16e67a8b62f8eed35692737c451c0396945f45931e7a7748f5c4e1614518cf	f3a1adfd3fd97414a425a2260da8d4ea942e75ea3056a476988545c9b49e776e
258	2026-08-19 16:27:31	NOTIFICATION_ALL_READ	{"user": "admin", "count": 6}	f3a1adfd3fd97414a425a2260da8d4ea942e75ea3056a476988545c9b49e776e	7a8b460403eadce11bc36f1021b234f9993dd7408fabbbf5a6786a7812ed0d03
259	2026-08-19 16:27:36.850384	ROBOT_STATUS_CHANGED	{"robot_code": "RB-BLR-01", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
260	2026-08-19 16:27:36	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-BLR-01", "source_entity_type": "ROBOT", "recipients_count": 0}	7a8b460403eadce11bc36f1021b234f9993dd7408fabbbf5a6786a7812ed0d03	6c69cf012c6f09d78dd6d723e9379760eb8b85e524d4a589ca4db5f4daa6ebff
261	2026-08-19 16:27:36.946569	ROBOT_STATUS_CHANGED	{"robot_code": "RB-BLR-02", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
262	2026-08-19 16:27:37	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-BLR-02", "source_entity_type": "ROBOT", "recipients_count": 0}	6c69cf012c6f09d78dd6d723e9379760eb8b85e524d4a589ca4db5f4daa6ebff	c4b7b104347e84f8348583991c6532279e1164f5649a35dbd5b639c93541b24c
263	2026-08-19 16:27:37.024246	ROBOT_STATUS_CHANGED	{"robot_code": "RB-CHN-01", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
264	2026-08-19 16:27:37	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-CHN-01", "source_entity_type": "ROBOT", "recipients_count": 0}	c4b7b104347e84f8348583991c6532279e1164f5649a35dbd5b639c93541b24c	c314a32253d3d9718dd8bee64790c1f1e4664aa530dee6e2b11d6d6d962c3d14
265	2026-08-19 16:27:37.108928	ROBOT_STATUS_CHANGED	{"robot_code": "RB-BOM-01", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
266	2026-08-19 16:27:37	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-BOM-01", "source_entity_type": "ROBOT", "recipients_count": 0}	c314a32253d3d9718dd8bee64790c1f1e4664aa530dee6e2b11d6d6d962c3d14	e6141939e935846c2b39bf357f86c5427e43f2dc4f7812d0a7d3fed38c084160
267	2026-08-19 16:27:37.22809	ROBOT_STATUS_CHANGED	{"robot_code": "RB-DEL-01", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
269	2026-08-19 16:27:37.340911	ROBOT_STATUS_CHANGED	{"robot_code": "RB-CCU-01", "previous_status": "CHARGING", "new_status": "AVAILABLE", "user_id": null, "notes": "Charging complete. Battery full."}	SYSTEM	SYSTEM
268	2026-08-19 16:27:37	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-DEL-01", "source_entity_type": "ROBOT", "recipients_count": 0}	e6141939e935846c2b39bf357f86c5427e43f2dc4f7812d0a7d3fed38c084160	bb92f2215f299261f7e0fbd054b825e22cb8b25777812a79c5b8341d76252667
270	2026-08-19 16:27:37	NOTIF_PUBLISHED_ROBOT_RECOVERED	{"event_type": "ROBOT_RECOVERED", "warehouse_id": null, "severity": "SUCCESS", "source_entity_id": "RB-CCU-01", "source_entity_type": "ROBOT", "recipients_count": 0}	bb92f2215f299261f7e0fbd054b825e22cb8b25777812a79c5b8341d76252667	d3eeb3f73ad2f6f8ca05e5547f67f3ad59997945fcb16e0ddef19cae6cf267d7
271	2026-08-19 16:28:14	SIMULATION_STARTED	{"simulation_id": 1, "warehouse_id": "WH-BLR-01", "by": "admin", "scenario": "NORMAL_OPERATIONS"}	d3eeb3f73ad2f6f8ca05e5547f67f3ad59997945fcb16e0ddef19cae6cf267d7	0c7d3a4bcc80727ad8bdb94b010ba6e6cad662eb36912e798ca556026286b615
272	2026-08-19 16:28:14	NOTIF_PUBLISHED_SIMULATION_STARTED	{"event_type": "SIMULATION_STARTED", "warehouse_id": "WH-BLR-01", "severity": "INFO", "source_entity_id": null, "source_entity_type": null, "recipients_count": 3}	0c7d3a4bcc80727ad8bdb94b010ba6e6cad662eb36912e798ca556026286b615	3c9e36b30879373f190b4174c86fd3a4303775fc3db5ee0923073c10abd39867
273	2026-08-19 16:28:31	NOTIFICATION_READ	{"notification_id": 21, "user": "admin"}	3c9e36b30879373f190b4174c86fd3a4303775fc3db5ee0923073c10abd39867	29c60f67617385bd75dbd8b46f7ee6b667f31986db1d5bbec3b43bdb2123d45d
274	2026-08-19 16:29:48.736953	OBSTACLE_CREATED	{"warehouse_id": "WH-BLR-01", "x": 5, "y": 1, "obstacle_type": "TEMPORARY_BLOCK"}	SYSTEM	SYSTEM
275	2026-08-19 16:29:54.55371	OBSTACLE_REMOVED	{"warehouse_id": "WH-BLR-01", "x": 5, "y": 1, "obstacle_id": 1}	SYSTEM	SYSTEM
276	2026-08-19 16:31:06	INCIDENT_RESOLVED_MANUALLY	{"incident_id": 1, "fingerprint": "BACKUP_VERIFICATION_FAILED", "user": "admin"}	SYSTEM	efcbb51fbc2d8aff53af06398f93f91855eb1185f2aac7172a8b2c53127286fd
277	2026-08-19 16:39:22	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T16:39:22.793859"}	efcbb51fbc2d8aff53af06398f93f91855eb1185f2aac7172a8b2c53127286fd	6cccc59666bcd2908337b64998ab0be87e00acc2c86ec1c2ea465c38507d5d1c
278	2026-08-19 16:39:22	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 3}	6cccc59666bcd2908337b64998ab0be87e00acc2c86ec1c2ea465c38507d5d1c	64c0c8e4d5afeb393cf0bbeef2e712e3e13ac722e7feff7779b6f5b5f20c9a87
279	2026-08-19 16:39:28	NOTIFICATION_READ	{"notification_id": 24, "user": "admin"}	64c0c8e4d5afeb393cf0bbeef2e712e3e13ac722e7feff7779b6f5b5f20c9a87	08da05dc5b6c190b5b86f71fb25c06054b5f26a44f3bd4de3dcf56f6265544fb
280	2026-08-19 16:56:00	user_created	{"new_username": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "created_by": "admin", "timestamp": "2026-08-19"}	08da05dc5b6c190b5b86f71fb25c06054b5f26a44f3bd4de3dcf56f6265544fb	f4a59cd7196e8cea14d0edf336828719a786e9188dccc30974b849e64fa2269e
281	2026-08-19 16:56:00	NOTIF_PUBLISHED_NEW_USER_CREATED	{"event_type": "NEW_USER_CREATED", "warehouse_id": null, "severity": "WARNING", "source_entity_id": null, "source_entity_type": null, "recipients_count": 4}	f4a59cd7196e8cea14d0edf336828719a786e9188dccc30974b849e64fa2269e	3adcc5577d3efca2964c639eff7ac0c057f377fcc79ed2d9a0ab206dd7af4209
282	2026-08-19 18:12:19	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:12:19.857412"}	3adcc5577d3efca2964c639eff7ac0c057f377fcc79ed2d9a0ab206dd7af4209	e19c1a3e239dc8fdcd4d14f74b8cc12b847b65c7bee7e01abc501f69823d01aa
283	2026-08-19 18:12:20	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	e19c1a3e239dc8fdcd4d14f74b8cc12b847b65c7bee7e01abc501f69823d01aa	eeed30e99aa840648ac3ae5cc3dd96570fb23a03a5c77ff431a2ec3d2ce01284
284	2026-08-19 18:13:00	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:13:00.938316"}	eeed30e99aa840648ac3ae5cc3dd96570fb23a03a5c77ff431a2ec3d2ce01284	0b80dbccc447edf681057cbc46fb63b52486bdc0be2a39ca49f3e4fb78701909
285	2026-08-19 18:13:00	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	0b80dbccc447edf681057cbc46fb63b52486bdc0be2a39ca49f3e4fb78701909	d718983d2a47c0ddea163f826e995e9b5aa260843a697fbfc83b93a6f2447eea
286	2026-08-19 18:13:53	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:13:53.997559"}	d718983d2a47c0ddea163f826e995e9b5aa260843a697fbfc83b93a6f2447eea	2de2207d7224df08fdf4548ed162293b1c9595a3bf2a9ab13bab021726ef0811
287	2026-08-19 18:13:54	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	2de2207d7224df08fdf4548ed162293b1c9595a3bf2a9ab13bab021726ef0811	311d3d12aebb6ca19d5ec620332601378c362865ca52d63f3a300c2f2a6a11bc
288	2026-08-19 18:15:14	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:15:14.502098"}	311d3d12aebb6ca19d5ec620332601378c362865ca52d63f3a300c2f2a6a11bc	f65684716b6341bf4e66197aa33ab55402078409c361bc906396f0a07d8024f6
289	2026-08-19 18:15:14	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	f65684716b6341bf4e66197aa33ab55402078409c361bc906396f0a07d8024f6	a71fae852576a5797b76918e4dc32e50dbe29865d8f28a9e5433bc44e8885465
290	2026-08-19 18:15:38	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	a71fae852576a5797b76918e4dc32e50dbe29865d8f28a9e5433bc44e8885465	63fe0d446f1fb4ece726c00da509130196210c382fd7e1eefb4bae3d0c7c12cd
291	2026-08-19 18:15:38	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	63fe0d446f1fb4ece726c00da509130196210c382fd7e1eefb4bae3d0c7c12cd	f6819ae4d92d0b49b761cadd40a768e135a5c9c53bcbeb06ea977fa36d31905c
292	2026-08-19 18:15:38	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	f6819ae4d92d0b49b761cadd40a768e135a5c9c53bcbeb06ea977fa36d31905c	cc74d3d94adb09258b81d075da1ed5ea32389045146affea7b259be74489b5b4
293	2026-08-19 18:15:38	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	cc74d3d94adb09258b81d075da1ed5ea32389045146affea7b259be74489b5b4	4a46ccb7b8c35f4aa66c68d9a3bfa7744ae762f150b92f7f4d3ab1fd7a657fca
294	2026-08-19 18:15:38	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	4a46ccb7b8c35f4aa66c68d9a3bfa7744ae762f150b92f7f4d3ab1fd7a657fca	d04d7a392879abd7927c7d5bedae937162c198430f0fab6d02903e38f5536013
295	2026-08-19 18:15:38	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	d04d7a392879abd7927c7d5bedae937162c198430f0fab6d02903e38f5536013	b3f8802fb93554429d38830aee4e8eafdcb7007157005bc7d55d3b1a38e5829b
296	2026-08-19 18:15:38	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	b3f8802fb93554429d38830aee4e8eafdcb7007157005bc7d55d3b1a38e5829b	c1b9ac5d54cce0c12722fd8e6e692d0b688cd197ba6f8476bbc1043769c3c260
297	2026-08-19 18:15:38	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	c1b9ac5d54cce0c12722fd8e6e692d0b688cd197ba6f8476bbc1043769c3c260	1e588e9060066dc6348eb1f3cc75fc9dcc8c8f6f4d2df24ee141d8b644f449c0
298	2026-08-19 18:15:38	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	1e588e9060066dc6348eb1f3cc75fc9dcc8c8f6f4d2df24ee141d8b644f449c0	d7f05fcd30c3a3bdce1e9b0f30e09480c299fd16206afbcb1d1d2f44b92c553c
299	2026-08-19 18:15:38	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	d7f05fcd30c3a3bdce1e9b0f30e09480c299fd16206afbcb1d1d2f44b92c553c	15e3d63836d68044eca66c15afaf3f0474702f80fbbf8ea0101095eb166542db
300	2026-08-19 18:15:38	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	15e3d63836d68044eca66c15afaf3f0474702f80fbbf8ea0101095eb166542db	531670123592987d5161a9681aadb635da44e684450c78cd10c3d42c126fbf0c
301	2026-08-19 18:15:38	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	531670123592987d5161a9681aadb635da44e684450c78cd10c3d42c126fbf0c	6095c669341b51b2877ca6b6a0def48945e93008b1a78210e8980942e5c97da3
302	2026-08-19 18:15:38	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	6095c669341b51b2877ca6b6a0def48945e93008b1a78210e8980942e5c97da3	00f51d343339f5b7ddcf0066cb9fc24ccbc0e07dae808d2cfd658f214171a1fd
303	2026-08-19 18:15:38	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	00f51d343339f5b7ddcf0066cb9fc24ccbc0e07dae808d2cfd658f214171a1fd	2dad6dc0e67870d1a00aa58ac86bb6fdfdb24b30a7191dcc562366de4c578523
304	2026-08-19 18:15:38	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	2dad6dc0e67870d1a00aa58ac86bb6fdfdb24b30a7191dcc562366de4c578523	46e6236b51067541603d0d7b3c940fe4205a9b690905047ec9b7f3a02ae7af88
305	2026-08-19 18:15:38	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	46e6236b51067541603d0d7b3c940fe4205a9b690905047ec9b7f3a02ae7af88	76d880d0a2318feb959909d10ed1a878f2ef0448726aab715b7c69ff96fec750
306	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	76d880d0a2318feb959909d10ed1a878f2ef0448726aab715b7c69ff96fec750	62cd7c673bbdf3f406bbf67751ff109cfe58e434934a818233d0064e8e67953d
307	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-23"}	62cd7c673bbdf3f406bbf67751ff109cfe58e434934a818233d0064e8e67953d	d40e7c3a4fcf4f2bb6d073df0717476cc2fd38d08b55455f637c677c0e460010
308	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-25"}	d40e7c3a4fcf4f2bb6d073df0717476cc2fd38d08b55455f637c677c0e460010	1f2e8aab8d65575c115f45802f26fc6aae2bb05bd0511d0e7a184056b41c3252
309	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	1f2e8aab8d65575c115f45802f26fc6aae2bb05bd0511d0e7a184056b41c3252	5d541eb7f2f4fc4519c1e09e8d8b39cee774ee0265c4a205c084611d5c9d7a0b
310	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	5d541eb7f2f4fc4519c1e09e8d8b39cee774ee0265c4a205c084611d5c9d7a0b	837406784cfadd65016f2cc98f219c60e828f45097c7efcb1c8a11a64b46454b
311	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	837406784cfadd65016f2cc98f219c60e828f45097c7efcb1c8a11a64b46454b	94c8608c8b0baf77390ac338f54adc8a0172dfa163d3fc140255ec65288fff7f
312	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	94c8608c8b0baf77390ac338f54adc8a0172dfa163d3fc140255ec65288fff7f	e573e46522cb6f1a5f768a7dd7a0ee33cce6d20187cb3eab2d7726af10506513
313	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-28"}	e573e46522cb6f1a5f768a7dd7a0ee33cce6d20187cb3eab2d7726af10506513	b40eae27265502bc6f947f6f20b8be346907fb32814be20bcda8d3ac9ec0a02a
314	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-28"}	b40eae27265502bc6f947f6f20b8be346907fb32814be20bcda8d3ac9ec0a02a	c66cf92527e84ad73bc9443aca375da3ca365cc9aab66a5c52d9d8831b726f8e
315	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-30"}	c66cf92527e84ad73bc9443aca375da3ca365cc9aab66a5c52d9d8831b726f8e	64c22127e8dc3b3e1f02c2e869d1f95e415ab2132341c3a006ef7da671f53c2c
316	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-01"}	64c22127e8dc3b3e1f02c2e869d1f95e415ab2132341c3a006ef7da671f53c2c	6673d9feedbdd49dc854be76955088a656d041e3a61e0dcc5709964b2b9c8779
317	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	6673d9feedbdd49dc854be76955088a656d041e3a61e0dcc5709964b2b9c8779	a17ed7e9731eb665fc6ce16d40624012205eb2cb777fc3049972817dd8816175
318	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	a17ed7e9731eb665fc6ce16d40624012205eb2cb777fc3049972817dd8816175	ae47aad32930f8f939d9be1d96cd52be733eb37b21401075c94324f569d9037a
319	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	ae47aad32930f8f939d9be1d96cd52be733eb37b21401075c94324f569d9037a	a8eb983f9109f7faa913029840fd24135db2fd8073748af0bf362d02a12cf4a2
320	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	a8eb983f9109f7faa913029840fd24135db2fd8073748af0bf362d02a12cf4a2	51486a253c2542be339f7bfbc9b96cc316179f067b762c041bc8830a582a33ba
321	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-04"}	51486a253c2542be339f7bfbc9b96cc316179f067b762c041bc8830a582a33ba	8234207c0686b693746554125369ffcdf680e8e0e7b276e5adc9f210d80a3dbc
322	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	8234207c0686b693746554125369ffcdf680e8e0e7b276e5adc9f210d80a3dbc	63c51ae45c43ab17c0df4bdb8eb80ac81369a4bef8a35f7dc5c45f55b28ff367
323	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-04"}	63c51ae45c43ab17c0df4bdb8eb80ac81369a4bef8a35f7dc5c45f55b28ff367	33993c605bcca9155e53e7b646e01e5cbec42bfc1d6a814982455157cfdcc622
324	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-05"}	33993c605bcca9155e53e7b646e01e5cbec42bfc1d6a814982455157cfdcc622	d70f9cc2f5629a0fdc0e1f25afd79601606aafbec6b195b959e051bd9494606a
325	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-05"}	d70f9cc2f5629a0fdc0e1f25afd79601606aafbec6b195b959e051bd9494606a	a808fbc7fd3ae3950bc0015d83c1ffd36c05e028b86978efc4b28cce007e31db
326	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-07"}	a808fbc7fd3ae3950bc0015d83c1ffd36c05e028b86978efc4b28cce007e31db	5f61643acd97135ef3244e84eeb5df24e6683c0bf0b3ea813ff0e74c2807fa94
327	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-08"}	5f61643acd97135ef3244e84eeb5df24e6683c0bf0b3ea813ff0e74c2807fa94	ba6847bc57ac904bd21effe6ed325a405b4b988f51e73c74a37c04b5f0b6d788
328	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-10"}	ba6847bc57ac904bd21effe6ed325a405b4b988f51e73c74a37c04b5f0b6d788	1cb3f7b7aa63c935a51d853bcb9de906549d0865aa8407cd2359f197cb72e881
329	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	1cb3f7b7aa63c935a51d853bcb9de906549d0865aa8407cd2359f197cb72e881	d0dfaeed0b92df98380bec6b98b26d34cd5f5a26abab2baff488567bc9a158f7
330	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-11"}	d0dfaeed0b92df98380bec6b98b26d34cd5f5a26abab2baff488567bc9a158f7	437356efe50bc32705efdd59733bbe7facaa88d35ece073c46fa20aefe265dec
331	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	437356efe50bc32705efdd59733bbe7facaa88d35ece073c46fa20aefe265dec	221be1e6720b41eaef4170574048d92b27859427591d48e883a3c62d7cf20eb9
332	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-11"}	221be1e6720b41eaef4170574048d92b27859427591d48e883a3c62d7cf20eb9	00db34f1d595beab1d522d1288838045ee422738aa4147f70c1b638c21555d97
333	2026-08-19 18:15:39	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	00db34f1d595beab1d522d1288838045ee422738aa4147f70c1b638c21555d97	4a84191919383f69dacbecfa90c91ebe2a04732f8bd690ecf3b3628b32108f82
334	2026-08-19 18:15:39	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	4a84191919383f69dacbecfa90c91ebe2a04732f8bd690ecf3b3628b32108f82	48c1ffb88bb4013b435ddc9a3a7c275c3468ba3b606627f0f95cfd697368633f
335	2026-08-19 18:15:39	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	48c1ffb88bb4013b435ddc9a3a7c275c3468ba3b606627f0f95cfd697368633f	c2d84f1bff839722885aa887c3d0350057e241cbfa49a3dbca805a617984bb93
336	2026-08-19 18:15:46	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:15:46.081142"}	c2d84f1bff839722885aa887c3d0350057e241cbfa49a3dbca805a617984bb93	c9faae26679f848d55ddbcfcee834cc64f9f9119438c4df8b97c70512db50556
337	2026-08-19 18:15:46	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	c9faae26679f848d55ddbcfcee834cc64f9f9119438c4df8b97c70512db50556	af8c2df265030e5329bd0dee2598c1d07a8888d2bbaae3c6b90a82e0bca1448e
338	2026-08-19 18:16:00	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:16:00.630796"}	af8c2df265030e5329bd0dee2598c1d07a8888d2bbaae3c6b90a82e0bca1448e	70fc01ae12c366fc6b94b101a43a311dfa9187df7f415fa58ef429254b2e76bb
339	2026-08-19 18:16:00	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	70fc01ae12c366fc6b94b101a43a311dfa9187df7f415fa58ef429254b2e76bb	262fca8f4a88f83e1a99d87c94c58ca719123e3cdfa8d3e25208374f6377489d
340	2026-08-19 18:16:02	AI_ASSISTANT_QUERY	{"user": "admin", "query": "Show me the robot fleet status", "warehouse_id": "WH-BLR-01"}	262fca8f4a88f83e1a99d87c94c58ca719123e3cdfa8d3e25208374f6377489d	73c358211f1923db40480afbd9110cef4f00d271c5b200d033f5a6af4af30c82
341	2026-08-19 18:16:05	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:16:05.031826"}	73c358211f1923db40480afbd9110cef4f00d271c5b200d033f5a6af4af30c82	1719b5e0d4343b262362895b702e4af49023efad6dadd4b7709d142d2b2790b1
342	2026-08-19 18:16:05	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	1719b5e0d4343b262362895b702e4af49023efad6dadd4b7709d142d2b2790b1	e5501cbf84486da786bb158a140a1304e1d74eb1e30849850e1ccdc3d2976e90
343	2026-08-19 18:16:06.217563	SCENARIO_CREATED	{"scenario_id": 1, "name": "Surge Flow Simulation", "created_by": "admin"}	SYSTEM	SYSTEM
345	2026-08-19 18:17:22	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	SYSTEM	a15b2e9a83c2c502372c913f3dbb5d694e2d568e2015f3db53095b504736e59f
346	2026-08-19 18:17:22	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	a15b2e9a83c2c502372c913f3dbb5d694e2d568e2015f3db53095b504736e59f	ef39dab8e4dc838ce36c105a643df2714a405dfb0f8a3bc2f3608d5810d94881
347	2026-08-19 18:17:22	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	ef39dab8e4dc838ce36c105a643df2714a405dfb0f8a3bc2f3608d5810d94881	ea8453207c83c9ccb9bb5481e0fdfcd013682b47aa239ec8724cdcb88ce1c5c5
348	2026-08-19 18:17:22	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	ea8453207c83c9ccb9bb5481e0fdfcd013682b47aa239ec8724cdcb88ce1c5c5	7b3f79637f6a5e49f99efa995e2669795049671491ee5b6d3474733d57559dc2
349	2026-08-19 18:17:22	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	7b3f79637f6a5e49f99efa995e2669795049671491ee5b6d3474733d57559dc2	a4bb2fc22b24dd3911d5c547c9dd31fb89fac6b1c0e902ef17d3898faab7182f
350	2026-08-19 18:17:22	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	a4bb2fc22b24dd3911d5c547c9dd31fb89fac6b1c0e902ef17d3898faab7182f	3c4dcf86d98e90865f6ba620e8bf9705ec06b0c5abfacdc3cc66c3f65f381369
351	2026-08-19 18:17:22	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	3c4dcf86d98e90865f6ba620e8bf9705ec06b0c5abfacdc3cc66c3f65f381369	d55314e0713e55deb76573055ccdd5362c026a1a547b86a7dc911500596a79bf
352	2026-08-19 18:17:22	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	d55314e0713e55deb76573055ccdd5362c026a1a547b86a7dc911500596a79bf	67f0ec8a897c5f7a9c3f44dff133b3358a03c75592088c64a92850afe3c5765e
353	2026-08-19 18:17:22	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	67f0ec8a897c5f7a9c3f44dff133b3358a03c75592088c64a92850afe3c5765e	8f7d60def0e9f8d8ad8d2bd6a92f0931c719a461ca183b0c371df0029d7a76ce
354	2026-08-19 18:17:22	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	8f7d60def0e9f8d8ad8d2bd6a92f0931c719a461ca183b0c371df0029d7a76ce	c6a605221db4ab3fef2e8ccd798d2e472c0ed320d8c0358b270b82803145e817
355	2026-08-19 18:17:22	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	c6a605221db4ab3fef2e8ccd798d2e472c0ed320d8c0358b270b82803145e817	794bbd9f75873257b64aeadd916128bf9a2ad6cf26aa23841afe1764f7469caa
356	2026-08-19 18:17:22	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	794bbd9f75873257b64aeadd916128bf9a2ad6cf26aa23841afe1764f7469caa	d2fd631d0e7047ff5900a6b78df0a53702da16a1b8c2efc9ad275da838702a7d
357	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	d2fd631d0e7047ff5900a6b78df0a53702da16a1b8c2efc9ad275da838702a7d	eaac40e1635dc0d78bc853ceb37b8ce4e5825214060ed7f85cda93ce2af35aab
358	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	eaac40e1635dc0d78bc853ceb37b8ce4e5825214060ed7f85cda93ce2af35aab	6085be2b814756f0e11064b8bd7980b2077af0e0236df5af4998384a1dd9fb86
359	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	6085be2b814756f0e11064b8bd7980b2077af0e0236df5af4998384a1dd9fb86	8d125f709386636f5dc5cb74abfd3a504bd316207d71bd3e0e51f80c5672f7b9
360	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	8d125f709386636f5dc5cb74abfd3a504bd316207d71bd3e0e51f80c5672f7b9	b8c54ecc3e6e6cf6c591fbddc8c8a301c3b51331664774e7acfe691b2354f8af
361	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	b8c54ecc3e6e6cf6c591fbddc8c8a301c3b51331664774e7acfe691b2354f8af	633de2f4327465bd9ddbbc85fde0ff2457e92299f0a1af4ac20619ebab81952e
362	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	633de2f4327465bd9ddbbc85fde0ff2457e92299f0a1af4ac20619ebab81952e	92dea68919f5bf4c78a2db072e34ef52f1da24f271c51b0e17b9b9400a2f67ae
363	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-26"}	92dea68919f5bf4c78a2db072e34ef52f1da24f271c51b0e17b9b9400a2f67ae	d57b577de5adc75a6c5c47015f9cc00042f4a07f4148b4602992888633f077a7
364	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-28"}	d57b577de5adc75a6c5c47015f9cc00042f4a07f4148b4602992888633f077a7	738f80dea5f10b7a3bb3e3a712bbae8e23fdb1fad499e14a65f95bd68c224cd3
365	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	738f80dea5f10b7a3bb3e3a712bbae8e23fdb1fad499e14a65f95bd68c224cd3	2d1fb16826ea72a812a0ce7204d9f8cb34921b0e8ca4da499820999e954db7b6
366	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	2d1fb16826ea72a812a0ce7204d9f8cb34921b0e8ca4da499820999e954db7b6	26dbc6f51195ccf99bfd4443772a83fa63cd32535404d78282802a8faf639199
367	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-30"}	26dbc6f51195ccf99bfd4443772a83fa63cd32535404d78282802a8faf639199	028bd37676dbc7e7cfcbb448011cd35b0e00ff0517734b1c02dd5f592bb4cead
368	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-31"}	028bd37676dbc7e7cfcbb448011cd35b0e00ff0517734b1c02dd5f592bb4cead	ace0ec7eae3084f426d4e591c348e6b8df5772b5baa27ecaca87be2970b70edc
369	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-31"}	ace0ec7eae3084f426d4e591c348e6b8df5772b5baa27ecaca87be2970b70edc	4af2305bbf417e9e3ae66ab658b47c161acf5e6948b82a5abb1ab018c7356cd8
370	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-01"}	4af2305bbf417e9e3ae66ab658b47c161acf5e6948b82a5abb1ab018c7356cd8	e24797d338080a5052c49a8bcdb242921688c25df8bbea34da1331f211ad8979
371	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-02"}	e24797d338080a5052c49a8bcdb242921688c25df8bbea34da1331f211ad8979	4a707a3bcc034bda1aac3e3a853d9fc608e5e7773a63c7dcdfa19157a5ebe18b
372	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-02"}	4a707a3bcc034bda1aac3e3a853d9fc608e5e7773a63c7dcdfa19157a5ebe18b	b0491d6717f56d3c22e64d93359356e7b0bbb8679aefaf780f01d46d1c206908
373	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	b0491d6717f56d3c22e64d93359356e7b0bbb8679aefaf780f01d46d1c206908	2947a76ef29adbdee9a9d5e8944c94eeab8ea2d20d53d10758f42ce5aa8feda1
374	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-03"}	2947a76ef29adbdee9a9d5e8944c94eeab8ea2d20d53d10758f42ce5aa8feda1	fbecc4b5d7447f5b5cc1837f20e3ce79a2a87d123c78009ef153f490cda3a470
375	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	fbecc4b5d7447f5b5cc1837f20e3ce79a2a87d123c78009ef153f490cda3a470	efd152cfbe54da4efe40c5ef6071ba4fba15c2fd86264480245f9322a5451a73
376	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	efd152cfbe54da4efe40c5ef6071ba4fba15c2fd86264480245f9322a5451a73	eca411c5b0f2b73f6b5f88b9761ad202bdb46351fd464f051d7e5048f248965d
377	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	eca411c5b0f2b73f6b5f88b9761ad202bdb46351fd464f051d7e5048f248965d	0072fbcee043bafcf1ed78920443506c4fa1a543affab8f8b3016a89ecb13a4b
378	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	0072fbcee043bafcf1ed78920443506c4fa1a543affab8f8b3016a89ecb13a4b	9cade6fea8d69133d23130f162b3ac8a3bb13a311d9f84d9ab0bc39e78cbc027
379	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-04"}	9cade6fea8d69133d23130f162b3ac8a3bb13a311d9f84d9ab0bc39e78cbc027	9565ea18eda1d8728844a47c192b1783396e99903a748023054516348eb307a4
380	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-05"}	9565ea18eda1d8728844a47c192b1783396e99903a748023054516348eb307a4	58d6e5c81acaa0595c64c092e756aff406fe36328309e57cb1d8d75f814047e0
381	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	58d6e5c81acaa0595c64c092e756aff406fe36328309e57cb1d8d75f814047e0	f67aa5c8f21f254d38856e0f26202ae8b7ffe45339604eb07815e9dea8363fac
382	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-07"}	f67aa5c8f21f254d38856e0f26202ae8b7ffe45339604eb07815e9dea8363fac	9514af7dad3f958aab3c483773495dc7c99b7c27cbbce1cb7a70540b04efa195
383	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-07"}	9514af7dad3f958aab3c483773495dc7c99b7c27cbbce1cb7a70540b04efa195	6d8ac2773640b4c6b05b2296b9dc4761012f9525c62857fc148fd3abbf9654a5
384	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-07"}	6d8ac2773640b4c6b05b2296b9dc4761012f9525c62857fc148fd3abbf9654a5	75e7258f6cba4d83b3141acf554394ea8f0768750cd7eaaf8e1da479fdc3f349
385	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-08"}	75e7258f6cba4d83b3141acf554394ea8f0768750cd7eaaf8e1da479fdc3f349	2c94cd0f726574b13fd9983468d6b03fb1ee3f1a697e801732013a08042d6072
386	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	2c94cd0f726574b13fd9983468d6b03fb1ee3f1a697e801732013a08042d6072	bec243de89c7c0f68dc9f226f841008b3b5bc3c0777efb02f781dc77c78b0ae5
387	2026-08-19 18:17:23	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-10"}	bec243de89c7c0f68dc9f226f841008b3b5bc3c0777efb02f781dc77c78b0ae5	272bc038f75250a1a46beb7bcb766d54deadd68a748d1429f194f1c31ad13bd3
388	2026-08-19 18:17:23	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	272bc038f75250a1a46beb7bcb766d54deadd68a748d1429f194f1c31ad13bd3	b6e360d166dc38e3125b64093b628830d124b97292dc626b01809bc0582afc4d
389	2026-08-19 18:17:23	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	b6e360d166dc38e3125b64093b628830d124b97292dc626b01809bc0582afc4d	014e3a02de7144ced93272ee2babd8d3e72525fa351c442a4b0957cebb6c9f88
390	2026-08-19 18:17:29	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:17:29.371138"}	014e3a02de7144ced93272ee2babd8d3e72525fa351c442a4b0957cebb6c9f88	5efa902f7546eadc04176f07bb768efb1d04196e51107e13b47e9c9a00ea7dca
392	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "queue_warning_depth", "old_value": 10.0, "new_value": 10.0, "user": "admin"}	b9ce4a9e5df88a3595fe13446252d926b77a1ad089cc63cd42e44231ca889cca	d9c509473f25a1d3e76ca5a357371fb98e2550f4d18caf5635a48c952ef2de1e
399	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "backup_age_critical_hours", "old_value": 48.0, "new_value": 48.0, "user": "admin"}	df0dae4acc6fd7297bc2277f865ff2a740cff8ffca6f210fa4b48874e3a12684	65e82090dab8a3552c1ffc9e2df9a9bef243f8b2312c31646955c23957e4c37b
391	2026-08-19 18:17:29	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	5efa902f7546eadc04176f07bb768efb1d04196e51107e13b47e9c9a00ea7dca	b9ce4a9e5df88a3595fe13446252d926b77a1ad089cc63cd42e44231ca889cca
393	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "queue_critical_depth", "old_value": 50.0, "new_value": 50.0, "user": "admin"}	d9c509473f25a1d3e76ca5a357371fb98e2550f4d18caf5635a48c952ef2de1e	716e4ca1da983633d19add55e13e1fa49400665919ddf2193b4d151438c86ad0
394	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "api_latency_warning_ms", "old_value": 300.0, "new_value": 350.0, "user": "admin"}	716e4ca1da983633d19add55e13e1fa49400665919ddf2193b4d151438c86ad0	14b885044481607a280367fc4a3e622e149b338df6a46a13b98ceee15736cbac
400	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "worker_stale_timeout_seconds", "old_value": 60.0, "new_value": 60.0, "user": "admin"}	65e82090dab8a3552c1ffc9e2df9a9bef243f8b2312c31646955c23957e4c37b	96fe26aa5d0dbdab38c745c01a12d75a25b9fc22f6422578058311b535da6b1a
401	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "api_error_rate_warning_pct", "old_value": 5.0, "new_value": 5.0, "user": "admin"}	96fe26aa5d0dbdab38c745c01a12d75a25b9fc22f6422578058311b535da6b1a	d92590da669711e82da055065257db8b3a34b12498c0678ce5fd1d429bd2864b
403	2026-08-19 18:17:40	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:17:40.657961"}	530b6d0ce4b7f0a2583f31fc783c1453bd0b2af7d1085620b4bba1107be33422	9060ed672b9eb7f928d8093e314b4aee963b81e006237d01f1d0cbc0a9b7105d
406	2026-08-19 18:17:57	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "127.0.0.1", "time": "2026-08-19T18:17:57.442178"}	4e0edde8b52f486a242eaf791039b2b7c7e07aa4246c026787070d33b174862e	6148d774f14dc8296629d64bcfaae98c96cb0f66350dad1838a1e7ed5eac5cd7
395	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "api_latency_critical_ms", "old_value": 1000.0, "new_value": 1000.0, "user": "admin"}	14b885044481607a280367fc4a3e622e149b338df6a46a13b98ceee15736cbac	3aa2f49cb8ac878b3712fee9d77ffb1122da2585d58d77a894c9b1d22e327c2a
402	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "api_error_rate_critical_pct", "old_value": 15.0, "new_value": 15.0, "user": "admin"}	d92590da669711e82da055065257db8b3a34b12498c0678ce5fd1d429bd2864b	530b6d0ce4b7f0a2583f31fc783c1453bd0b2af7d1085620b4bba1107be33422
404	2026-08-19 18:17:40	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	9060ed672b9eb7f928d8093e314b4aee963b81e006237d01f1d0cbc0a9b7105d	8b475cc383d8d54a462558ab29294db6d0839aea3ab9e1666eb1afa2bd5269d5
409	2026-08-19 18:18:08.050878	EXPERIMENT_CREATED	{"experiment_id": 2, "name": "OR-Tools Priority Test", "created_by": "admin"}	SYSTEM	SYSTEM
396	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "database_latency_warning_ms", "old_value": 100.0, "new_value": 100.0, "user": "admin"}	3aa2f49cb8ac878b3712fee9d77ffb1122da2585d58d77a894c9b1d22e327c2a	af5ff1ac8af7d13e3def58ecaebb930051a8ea704c5d8f442b61f826de0f718c
405	2026-08-19 18:17:55	AI_ASSISTANT_QUERY	{"user": "admin", "query": "Show me the robot fleet status", "warehouse_id": "WH-BLR-01"}	8b475cc383d8d54a462558ab29294db6d0839aea3ab9e1666eb1afa2bd5269d5	4e0edde8b52f486a242eaf791039b2b7c7e07aa4246c026787070d33b174862e
397	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "database_latency_critical_ms", "old_value": 500.0, "new_value": 500.0, "user": "admin"}	af5ff1ac8af7d13e3def58ecaebb930051a8ea704c5d8f442b61f826de0f718c	1c12d552614543aff0a7461d1a4d4d670e14c63dfff43c8bf9acd195866a2ef9
398	2026-08-19 18:17:37	THRESHOLD_UPDATED	{"key": "backup_age_warning_hours", "old_value": 26.0, "new_value": 26.0, "user": "admin"}	1c12d552614543aff0a7461d1a4d4d670e14c63dfff43c8bf9acd195866a2ef9	df0dae4acc6fd7297bc2277f865ff2a740cff8ffca6f210fa4b48874e3a12684
408	2026-08-19 18:18:05.580504	SCENARIO_CREATED	{"scenario_id": 2, "name": "Surge Flow Simulation", "created_by": "admin"}	SYSTEM	SYSTEM
407	2026-08-19 18:17:57	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	6148d774f14dc8296629d64bcfaae98c96cb0f66350dad1838a1e7ed5eac5cd7	9efc05d6f6039935fb71c913e2720759388a448334b60c431c0fcbbd0d90c812
410	2026-08-19 18:18:36	user_login	{"username": "admin", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:18:36.665352"}	SYSTEM	d0c7bb429779e296a77a7ffd079d9493caac1c1c594a24383716f3eb98ad4600
411	2026-08-19 18:18:36	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "1", "source_entity_type": "USER", "recipients_count": 4}	d0c7bb429779e296a77a7ffd079d9493caac1c1c594a24383716f3eb98ad4600	cf12530b98100b38c6d50ca9cc623a1c9fcd539e9767bc8f91409a4a06f6a288
412	2026-08-19 18:18:37	warehouse_created	{"warehouse_id": "WH-BLR-01", "name": "Bangalore Fulfillment Center"}	cf12530b98100b38c6d50ca9cc623a1c9fcd539e9767bc8f91409a4a06f6a288	80dadf5dbacd807041756f5f6b8d1eb8921552893f80b3f9a53c8449936ce448
413	2026-08-19 18:18:37	warehouse_created	{"warehouse_id": "WH-CHN-01", "name": "Chennai Port Logistics Hub"}	80dadf5dbacd807041756f5f6b8d1eb8921552893f80b3f9a53c8449936ce448	7d348b50f9e8cb182a93905210b8cda3651de8a6b097706bf401dab1b2547536
414	2026-08-19 18:18:37	warehouse_created	{"warehouse_id": "WH-BOM-01", "name": "Mumbai Container Terminal"}	7d348b50f9e8cb182a93905210b8cda3651de8a6b097706bf401dab1b2547536	cbbd302965c24d6f44e1ebcabe114bb707b1136e06f9a31bc60afac34f4deda8
415	2026-08-19 18:18:37	warehouse_created	{"warehouse_id": "WH-DEL-01", "name": "Delhi NCR Logistics Park"}	cbbd302965c24d6f44e1ebcabe114bb707b1136e06f9a31bc60afac34f4deda8	8c6b34c4dd3b0407e715e70d5001deab8e036f12e03587a50608d11bb41027bc
416	2026-08-19 18:18:37	warehouse_created	{"warehouse_id": "WH-CCU-01", "name": "Kolkata Gateway Depot"}	8c6b34c4dd3b0407e715e70d5001deab8e036f12e03587a50608d11bb41027bc	a9a8d2810ccdaa39bffee59f175dcf759b6b81327ef430bb0cb02e9a3b7c250e
417	2026-08-19 18:18:37	item_created	{"item_id": "ITM-CPU-01", "name": "AMD Ryzen 9 7900X Processor"}	a9a8d2810ccdaa39bffee59f175dcf759b6b81327ef430bb0cb02e9a3b7c250e	69d7df2e0c8413d73eebdae86c3d46cf792db4ac6175c1e8628deba3cf317c7f
418	2026-08-19 18:18:37	item_created	{"item_id": "ITM-GPU-01", "name": "Nvidia RTX 4080 Founders Edition"}	69d7df2e0c8413d73eebdae86c3d46cf792db4ac6175c1e8628deba3cf317c7f	44db245d3263c1e72424a3d3658483d21801fbcab239c7490d50affed9aa848b
419	2026-08-19 18:18:37	item_created	{"item_id": "ITM-RAM-01", "name": "Corsair DDR5 32GB 6000MHz RAM"}	44db245d3263c1e72424a3d3658483d21801fbcab239c7490d50affed9aa848b	70d186a303be7849e4c7cabd3bfcb0d30dfe1de250c9a5bca5f857b0d28d2522
420	2026-08-19 18:18:37	item_created	{"item_id": "ITM-SSD-01", "name": "Samsung 990 Pro 2TB NVMe SSD"}	70d186a303be7849e4c7cabd3bfcb0d30dfe1de250c9a5bca5f857b0d28d2522	a67e271fe615f0bdedc2c6ceefa8bea17e59e274307831bb48b18c80b95cf54b
421	2026-08-19 18:18:37	item_created	{"item_id": "ITM-HDD-01", "name": "WD Red Pro 8TB NAS Hard Drive"}	a67e271fe615f0bdedc2c6ceefa8bea17e59e274307831bb48b18c80b95cf54b	14706aceb663445c36a18d8791232222dc33941918eb570f9f7d1d472f18d3af
422	2026-08-19 18:18:37	item_created	{"item_id": "ITM-CHG-01", "name": "Anker 100W GaN Wall Charger"}	14706aceb663445c36a18d8791232222dc33941918eb570f9f7d1d472f18d3af	cad4e5177a2e65dc3d7f79a59c9f7e42b1444ca7f02806d3e28fe793e3c43e3b
423	2026-08-19 18:18:37	item_created	{"item_id": "ITM-CBL-01", "name": "Apple USB-C Braided Cable 2m"}	cad4e5177a2e65dc3d7f79a59c9f7e42b1444ca7f02806d3e28fe793e3c43e3b	cb73b6ccd495d9cfc8991b4c765a94ab184aca78f481635f02ae2925e9f9ce99
424	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-19"}	cb73b6ccd495d9cfc8991b4c765a94ab184aca78f481635f02ae2925e9f9ce99	84576cc64d2dfcfbfa5425a3af3b579dfb7d2b14ff58faef67f093eee4aab73c
425	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-20"}	84576cc64d2dfcfbfa5425a3af3b579dfb7d2b14ff58faef67f093eee4aab73c	b6fb5bd318d28d956bfb07e6b45f351da5b8ee87e05cb9a74274775decb97dbc
426	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	b6fb5bd318d28d956bfb07e6b45f351da5b8ee87e05cb9a74274775decb97dbc	aa6b68e8f119561f7d8719b12f0b1d87b121cffa4f527265b7f99f5f24632d04
427	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-21"}	aa6b68e8f119561f7d8719b12f0b1d87b121cffa4f527265b7f99f5f24632d04	53a5c17346f01e6834b963d65a9d358fe0c4541a3cdcf5f478d1536b3dfae41f
428	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-07-23"}	53a5c17346f01e6834b963d65a9d358fe0c4541a3cdcf5f478d1536b3dfae41f	2292fe6ea5cd9ccac94f6cdeda1bd2fac1c03f2915b40f31d8ac47cb90b513b4
429	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-25"}	2292fe6ea5cd9ccac94f6cdeda1bd2fac1c03f2915b40f31d8ac47cb90b513b4	98463ca60130078bb3d6c53a3e8b1e837d095b5f6c3bdf03ced7f625f75a40e4
430	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	98463ca60130078bb3d6c53a3e8b1e837d095b5f6c3bdf03ced7f625f75a40e4	dc5f93cc61fc0a9143913a017177b8ca3af14cdd7720ee5f80df7f026b5d4695
431	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-26"}	dc5f93cc61fc0a9143913a017177b8ca3af14cdd7720ee5f80df7f026b5d4695	4a02d94c42527b890d26d4629b8461bd8162632d064cc6ed01dac6a66ce60b09
432	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	4a02d94c42527b890d26d4629b8461bd8162632d064cc6ed01dac6a66ce60b09	cd57054dbc160886b23a38dceed9fd6727b2b92400b8229dd9ca4af1ce296df5
433	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-27"}	cd57054dbc160886b23a38dceed9fd6727b2b92400b8229dd9ca4af1ce296df5	ec5c2184e1799ba6fa24289d3d0a49dc1877f8ff8ba096c9517c4ff87631d1c3
434	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-28"}	ec5c2184e1799ba6fa24289d3d0a49dc1877f8ff8ba096c9517c4ff87631d1c3	c1a3f21b176623a019479a8c13181e2de72f424abececa463eb1d4e7c989409b
435	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-07-28"}	c1a3f21b176623a019479a8c13181e2de72f424abececa463eb1d4e7c989409b	d58a5e17e5c35adb3694f65db2bbbcc9d10e1061530a770ad1bdc57c53c0273e
436	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CHG-01", "quantity": 150, "date": "2026-07-31"}	d58a5e17e5c35adb3694f65db2bbbcc9d10e1061530a770ad1bdc57c53c0273e	9ab1ed9c2ba3b18fd25a4bf26ad18213812f59e802b26e39a55aa6500259fec2
437	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-01"}	9ab1ed9c2ba3b18fd25a4bf26ad18213812f59e802b26e39a55aa6500259fec2	3aa59c79dfb14c83fe97100d109d24e12a396b90d95a3b91c4e137f588856eb6
438	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-01"}	3aa59c79dfb14c83fe97100d109d24e12a396b90d95a3b91c4e137f588856eb6	3858c3b9bffac329155de63b956359dd96b2064d207c8f1c29aacb4eb745599d
439	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	3858c3b9bffac329155de63b956359dd96b2064d207c8f1c29aacb4eb745599d	7f31d1a9aa98f8568dae63217364207cfc89993b5a036f6f61733f0eeb571c03
440	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-02"}	7f31d1a9aa98f8568dae63217364207cfc89993b5a036f6f61733f0eeb571c03	359ae28b17bffc6c65b3da510ecb3034b485e7e695e400d851a51613946fa508
441	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-02"}	359ae28b17bffc6c65b3da510ecb3034b485e7e695e400d851a51613946fa508	fcb61169c4aae8cc9f81f466129f30b0b62a1c87ffd826d40314870bd7500097
442	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-02"}	fcb61169c4aae8cc9f81f466129f30b0b62a1c87ffd826d40314870bd7500097	3335384f1ab0a0bfd0503ca919b0d7f1efbb2ed91107b3c7777a9527128359e5
443	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-03"}	3335384f1ab0a0bfd0503ca919b0d7f1efbb2ed91107b3c7777a9527128359e5	5e90f288863737eee8e41776907b10a7e9b0d0267dd91213f5659c86a3638343
444	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-03"}	5e90f288863737eee8e41776907b10a7e9b0d0267dd91213f5659c86a3638343	974ed728e4e77b4f09d23a6da3fc3dc3e8efd90fee09ea2241cc11eacaa4e587
445	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	974ed728e4e77b4f09d23a6da3fc3dc3e8efd90fee09ea2241cc11eacaa4e587	0e7190eaa0009672f23a8b89f7676929d2311db35116ab57176eef50e78222b6
446	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CPU-01", "quantity": 45, "date": "2026-08-04"}	0e7190eaa0009672f23a8b89f7676929d2311db35116ab57176eef50e78222b6	ff7426f7f877c2676a60be3810dcd19bb8b7937ee22beddd5967ebe018d53d8c
447	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-RAM-01", "quantity": 75, "date": "2026-08-04"}	ff7426f7f877c2676a60be3810dcd19bb8b7937ee22beddd5967ebe018d53d8c	76735ac1fc739ef6e1396ee295a56b9e4c05c4613a77dafd77f131064f8df6da
448	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-05"}	76735ac1fc739ef6e1396ee295a56b9e4c05c4613a77dafd77f131064f8df6da	80a4b7898ec7277fbd01fb6cbef8a075ff9074968e5cd0fa95faa7212076f86b
449	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-05"}	80a4b7898ec7277fbd01fb6cbef8a075ff9074968e5cd0fa95faa7212076f86b	5384132a3fcdcd40c5962aadf644175c19ef87c5738e48efa5fa0623f98a4bad
450	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-DEL-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-05"}	5384132a3fcdcd40c5962aadf644175c19ef87c5738e48efa5fa0623f98a4bad	dac5bec3b72712407c72cd8b368e1e0ecef055e7bc2ab3e8f8e7c5ada5e31049
451	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-GPU-01", "quantity": 30, "date": "2026-08-06"}	dac5bec3b72712407c72cd8b368e1e0ecef055e7bc2ab3e8f8e7c5ada5e31049	9c3ed09c8631d5eba3e79dbf65a47a6314fd4523a94cc6f06de470760abed231
452	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-07"}	9c3ed09c8631d5eba3e79dbf65a47a6314fd4523a94cc6f06de470760abed231	0d18c479cf2d0b60262d46c1f83c045cbb7fee331c494367dbba56ffeadee58b
453	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-07"}	0d18c479cf2d0b60262d46c1f83c045cbb7fee331c494367dbba56ffeadee58b	6b30ad73ce42f6218e37cfe6403a983ae7cea8eb7affae2e27305593d5d3a10d
454	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-CCU-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-08"}	6b30ad73ce42f6218e37cfe6403a983ae7cea8eb7affae2e27305593d5d3a10d	bd0926a5d7963f7ea78d6f0ce6a33dd5f5e6aaec8366a7f7c9fbd77af9890fc2
455	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-09"}	bd0926a5d7963f7ea78d6f0ce6a33dd5f5e6aaec8366a7f7c9fbd77af9890fc2	b580b64241ad3d74d715c69e78f9d4e208d3d4df8d5483fa947463ac1aeaca33
456	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-11"}	b580b64241ad3d74d715c69e78f9d4e208d3d4df8d5483fa947463ac1aeaca33	c8fc2b3204b0f8645318fb713d6ee5b8b185db082af14a5aea15299c848cc41a
457	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-HDD-01", "quantity": 60, "date": "2026-08-11"}	c8fc2b3204b0f8645318fb713d6ee5b8b185db082af14a5aea15299c848cc41a	3b9ddcdf0f8b6d64d868ed7e6c0a26ac7a2508899b480e3edaad8bc73e6da065
458	2026-08-19 18:18:37	simulated_restock	{"warehouse_id": "WH-BOM-01", "item_id": "ITM-CBL-01", "quantity": 300, "date": "2026-08-11"}	3b9ddcdf0f8b6d64d868ed7e6c0a26ac7a2508899b480e3edaad8bc73e6da065	8e91b8bb3b6621f5621523d0797e6c4afaaa811a3ca15d53f6158687e8983f81
459	2026-08-19 18:18:37	shrinkage_flag	{"warehouse_id": "WH-BLR-01", "item_id": "ITM-GPU-01", "likely_cause": "UNUSUAL_OUTBOUND_ACTIVITY"}	8e91b8bb3b6621f5621523d0797e6c4afaaa811a3ca15d53f6158687e8983f81	b8afb06db9337587a5ea17c4ee08bf218005e1c9661b0f5c866f4cf2f7c9cdae
460	2026-08-19 18:18:37	shrinkage_flag	{"warehouse_id": "WH-CHN-01", "item_id": "ITM-CPU-01", "likely_cause": "POSSIBLE_DAMAGE_OR_WASTAGE"}	b8afb06db9337587a5ea17c4ee08bf218005e1c9661b0f5c866f4cf2f7c9cdae	c6cb39cc2324980ee0527fcd48ff8529f443a5d1ee6b25e8bcb47fb1c9974fb0
461	2026-08-19 18:18:42	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:18:42.478299"}	c6cb39cc2324980ee0527fcd48ff8529f443a5d1ee6b25e8bcb47fb1c9974fb0	7b3293a880c2d999fd0b8a48ffd50555aaa0eae81fcddee01e44279090c34977
462	2026-08-19 18:18:42	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	7b3293a880c2d999fd0b8a48ffd50555aaa0eae81fcddee01e44279090c34977	35beb386cf87fa1182dd1e595465ac0909f1f4859952d3ccb9ad9efd3c6798e8
463	2026-08-19 18:18:55	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:18:55.021150"}	35beb386cf87fa1182dd1e595465ac0909f1f4859952d3ccb9ad9efd3c6798e8	d104e3d0061c5e5e1e1ec830bff3895d5268037cb7887dd41651c3c1f87d77ad
464	2026-08-19 18:18:55	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	d104e3d0061c5e5e1e1ec830bff3895d5268037cb7887dd41651c3c1f87d77ad	6b08f93d89559d732823b510862a1d1e7017bdd7a12338a943693f6d5781fbcc
465	2026-08-19 18:19:02	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:19:02.389702"}	6b08f93d89559d732823b510862a1d1e7017bdd7a12338a943693f6d5781fbcc	7257f5339e9e691bd200d712805278f683ab7126e14891f6ce38cf8616521caa
467	2026-08-19 18:19:09	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:19:09.735218"}	7fad25bf848857d6b5d9ad403d4e64ef86f7f286d1f00359b194f8bd58d079a5	2ace31a93d787a786e15a72b1b5dfe8b58ffab391bd4781f37f6a46a63408132
470	2026-08-19 18:19:10	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	ef7d4dbf03a2d1ef98999e88e7ee61877d1c6e84e366463d6836b2ef60659026	da040ec2cc72d7060017ea500d426b82604662033170ab66526eb39a1d2abfe1
472	2026-08-19 18:19:10	NOTIF_PUBLISHED_AI_RECOMMENDATION_APPROVED	{"event_type": "AI_RECOMMENDATION_APPROVED", "warehouse_id": "WH-BLR-01", "severity": "SUCCESS", "source_entity_id": "None", "source_entity_type": "TASK", "recipients_count": 0}	357a3ff99012aec3c4b9b7cb59fa87ee9cc47851af0efd3702d90e25eca5dc3f	039ec9bc1dca81b3528705e53649cc419c92603b356fb72a2bb926139ec8e7e4
474	2026-08-19 18:19:11	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	f95f490be432c92ec6b5fd19e04fb55f0c408f1671c26981491c0115ef5921f0	1f857c450531a912d536e036a3716956d4062080fc6fde6a97c1483958506bea
466	2026-08-19 18:19:02	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	7257f5339e9e691bd200d712805278f683ab7126e14891f6ce38cf8616521caa	7fad25bf848857d6b5d9ad403d4e64ef86f7f286d1f00359b194f8bd58d079a5
468	2026-08-19 18:19:09	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "5", "source_entity_type": "USER", "recipients_count": 4}	2ace31a93d787a786e15a72b1b5dfe8b58ffab391bd4781f37f6a46a63408132	79f06ce9f12a0cf4ba69e9c01099e2c5576ece4c764fac7b19d01d463a6a5586
469	2026-08-19 18:19:10	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:19:10.685320"}	79f06ce9f12a0cf4ba69e9c01099e2c5576ece4c764fac7b19d01d463a6a5586	ef7d4dbf03a2d1ef98999e88e7ee61877d1c6e84e366463d6836b2ef60659026
471	2026-08-19 18:19:10	AI_RECOMMENDATION_APPROVED	{"recommendation_id": 1, "recommendation_type": "ANOMALY", "approved_by": "test_admin_hardened", "task_id": null, "notes": "Test approval"}	da040ec2cc72d7060017ea500d426b82604662033170ab66526eb39a1d2abfe1	357a3ff99012aec3c4b9b7cb59fa87ee9cc47851af0efd3702d90e25eca5dc3f
473	2026-08-19 18:19:11	user_login	{"username": "test_admin_hardened", "role": "admin", "method": "password", "ip": "testclient", "time": "2026-08-19T18:19:11.654934"}	039ec9bc1dca81b3528705e53649cc419c92603b356fb72a2bb926139ec8e7e4	f95f490be432c92ec6b5fd19e04fb55f0c408f1671c26981491c0115ef5921f0
475	2026-08-19 18:19:19	user_login	{"username": "test_ai_manager", "role": "manager", "method": "password", "ip": "testclient", "time": "2026-08-19T18:19:19.465179"}	1f857c450531a912d536e036a3716956d4062080fc6fde6a97c1483958506bea	76efbd53277cba7d5114f53c94bf77b9c3d99737be3c9a2e5278599dcf9e6da6
476	2026-08-19 18:19:19	NOTIF_PUBLISHED_USER_LOGIN	{"event_type": "USER_LOGIN", "warehouse_id": null, "severity": "INFO", "source_entity_id": "7", "source_entity_type": "USER", "recipients_count": 4}	76efbd53277cba7d5114f53c94bf77b9c3d99737be3c9a2e5278599dcf9e6da6	b7761744d1e888d1dfb52f1d35135c758f0afb0e726f65a78a8f75e3ef40945d
\.


--
-- Data for Name: backup_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.backup_records (id, backup_id, filename, created_at, size_bytes, sha256, status, storage_key, error_message, backup_type, started_at, completed_at, storage_provider, bucket, checksum_algorithm, verification_status, verification_at, restore_test_status, restore_test_at, retention_status, initiated_by, audit_ref) FROM stdin;
1	BK-DE66910CF7A81BD9	warehouse_postgres_2026-08-19_16-23-49.sql.gz	2026-08-19 16:23:49.107895	46585	48f2cc9f84bee2ff275907a3c519115b05f6e6f1a957051a41abf7e76644e0f4	FAILED	data/backups/warehouse_postgres_2026-08-19_16-23-49.sql.gz	B2 Upload failed: An error occurred (UnauthorizedAccess) when calling the PutObject operation: Seed signature is invalid	MANUAL	2026-08-19 16:23:49.097906	2026-08-19 16:23:52.565918	Local Fallback	harsha-warehouse-backups	SHA-256	PENDING	\N	PENDING	\N	ACTIVE	SYSTEM	\N
2	BK-375768E40DC6BF03	warehouse_postgres_2026-08-19_17-23-52.sql.gz	2026-08-19 17:23:52.607812	61597	ae289501cc4aa1493b1efe7878f6cb601d869132e2799a88011d7e54337b6074	FAILED	data/backups/warehouse_postgres_2026-08-19_17-23-52.sql.gz	B2 Upload failed: An error occurred (UnauthorizedAccess) when calling the PutObject operation: Seed signature is invalid	MANUAL	2026-08-19 17:23:52.604197	2026-08-19 17:23:55.780868	Local Fallback	harsha-warehouse-backups	SHA-256	PENDING	\N	PENDING	\N	ACTIVE	SYSTEM	\N
3	BK-250120BC0645B124	warehouse_postgres_2026-08-19_18-14-44.sql.gz	2026-08-19 18:14:44.048634	65704	5d86d3be297bf28af4fd6bf8471e7b4db6ea70946fc7ab22606897130bd86fb3	FAILED	data/backups/warehouse_postgres_2026-08-19_18-14-44.sql.gz	B2 Upload failed: An error occurred (UnauthorizedAccess) when calling the PutObject operation: Seed signature is invalid	MANUAL	2026-08-19 18:14:44.042598	2026-08-19 18:14:49.827991	Local Fallback	harsha-warehouse-backups	SHA-256	PENDING	\N	PENDING	\N	ACTIVE	SYSTEM	\N
4	BK-11A1897F330EED90	warehouse_postgres_2026-08-19_18-19-23.sql.gz	2026-08-19 18:19:23.219868	\N	\N	RUNNING	\N	\N	MANUAL	2026-08-19 18:19:23.21587	\N	Backblaze B2 Storage	harsha-warehouse-backups	SHA-256	PENDING	\N	PENDING	\N	ACTIVE	SYSTEM	\N
\.


--
-- Data for Name: digital_twin_simulations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.digital_twin_simulations (id, warehouse_id, simulation_status, simulation_time_seconds, speed_multiplier, seed, mode, scenario_type, tick_count, created_at, started_at, paused_at, stopped_at, completed_at, error_message, created_by) FROM stdin;
\.


--
-- Data for Name: experiment_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.experiment_runs (id, experiment_id, repetition_number, random_seed, status, started_at, completed_at, duration_seconds, error_message, metrics, created_at) FROM stdin;
\.


--
-- Data for Name: experiments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.experiments (id, scenario_id, experiment_name, description, status, algorithm_name, algorithm_version, configuration, random_seed, repetitions, started_at, completed_at, duration_seconds, created_by, error_message, metrics_summary, created_at) FROM stdin;
\.


--
-- Data for Name: health_thresholds; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.health_thresholds (id, key, value, description, created_at, updated_at) FROM stdin;
1	queue_warning_depth	10	Warning threshold for RabbitMQ queue depth	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.813743
2	queue_critical_depth	50	Critical threshold for RabbitMQ queue depth	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.851472
3	api_latency_warning_ms	350	Warning threshold for API request response time	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.859672
4	api_latency_critical_ms	1000	Critical threshold for API request response time	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.86669
5	database_latency_warning_ms	100	Warning threshold for Supabase DB response time	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.873688
6	database_latency_critical_ms	500	Critical threshold for Supabase DB response time	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.880688
7	backup_age_warning_hours	26	Warning threshold for backup age	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.887693
8	backup_age_critical_hours	48	Critical threshold for backup age	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.893694
9	worker_stale_timeout_seconds	60	Heartbeat threshold for stale Celery worker status	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.899689
10	api_error_rate_warning_pct	5	Warning threshold for API request error percentage	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.906689
11	api_error_rate_critical_pct	15	Critical threshold for API request error percentage	2026-08-19 18:14:39.012967	2026-08-19 18:17:37.91369
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (id, warehouse_id, item_id, location_id, on_hand, reserved, available, damaged, created_at, updated_at) FROM stdin;
246	WH-BLR-01	ITM-CPU-01	WH-WH-BLR-01-LOC-ITM-CPU-01-STORAGE	38	0	38	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
247	WH-BLR-01	ITM-GPU-01	WH-WH-BLR-01-LOC-ITM-GPU-01-STORAGE	32	0	32	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
248	WH-BLR-01	ITM-RAM-01	WH-WH-BLR-01-LOC-ITM-RAM-01-STORAGE	44	0	44	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
249	WH-BLR-01	ITM-SSD-01	WH-WH-BLR-01-LOC-ITM-SSD-01-STORAGE	60	0	60	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
250	WH-BLR-01	ITM-HDD-01	WH-WH-BLR-01-LOC-ITM-HDD-01-STORAGE	87	0	87	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
251	WH-BLR-01	ITM-CHG-01	WH-WH-BLR-01-LOC-ITM-CHG-01-STORAGE	136	0	136	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
252	WH-BLR-01	ITM-CBL-01	WH-WH-BLR-01-LOC-ITM-CBL-01-STORAGE	431	0	431	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
253	WH-CHN-01	ITM-CPU-01	WH-WH-CHN-01-LOC-ITM-CPU-01-STORAGE	42	0	42	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
254	WH-CHN-01	ITM-GPU-01	WH-WH-CHN-01-LOC-ITM-GPU-01-STORAGE	41	0	41	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
255	WH-CHN-01	ITM-RAM-01	WH-WH-CHN-01-LOC-ITM-RAM-01-STORAGE	48	0	48	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
256	WH-CHN-01	ITM-SSD-01	WH-WH-CHN-01-LOC-ITM-SSD-01-STORAGE	54	0	54	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
257	WH-CHN-01	ITM-HDD-01	WH-WH-CHN-01-LOC-ITM-HDD-01-STORAGE	83	0	83	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
258	WH-CHN-01	ITM-CHG-01	WH-WH-CHN-01-LOC-ITM-CHG-01-STORAGE	96	0	96	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
259	WH-CHN-01	ITM-CBL-01	WH-WH-CHN-01-LOC-ITM-CBL-01-STORAGE	412	0	412	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
260	WH-BOM-01	ITM-CPU-01	WH-WH-BOM-01-LOC-ITM-CPU-01-STORAGE	60	0	60	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
261	WH-BOM-01	ITM-GPU-01	WH-WH-BOM-01-LOC-ITM-GPU-01-STORAGE	38	0	38	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
262	WH-BOM-01	ITM-RAM-01	WH-WH-BOM-01-LOC-ITM-RAM-01-STORAGE	52	0	52	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
263	WH-BOM-01	ITM-SSD-01	WH-WH-BOM-01-LOC-ITM-SSD-01-STORAGE	52	0	52	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
264	WH-BOM-01	ITM-HDD-01	WH-WH-BOM-01-LOC-ITM-HDD-01-STORAGE	86	0	86	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
265	WH-BOM-01	ITM-CHG-01	WH-WH-BOM-01-LOC-ITM-CHG-01-STORAGE	115	0	115	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
266	WH-BOM-01	ITM-CBL-01	WH-WH-BOM-01-LOC-ITM-CBL-01-STORAGE	442	0	442	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
267	WH-DEL-01	ITM-CPU-01	WH-WH-DEL-01-LOC-ITM-CPU-01-STORAGE	49	0	49	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
268	WH-DEL-01	ITM-GPU-01	WH-WH-DEL-01-LOC-ITM-GPU-01-STORAGE	41	0	41	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
269	WH-DEL-01	ITM-RAM-01	WH-WH-DEL-01-LOC-ITM-RAM-01-STORAGE	44	0	44	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
270	WH-DEL-01	ITM-SSD-01	WH-WH-DEL-01-LOC-ITM-SSD-01-STORAGE	56	0	56	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
271	WH-DEL-01	ITM-HDD-01	WH-WH-DEL-01-LOC-ITM-HDD-01-STORAGE	81	0	81	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
272	WH-DEL-01	ITM-CHG-01	WH-WH-DEL-01-LOC-ITM-CHG-01-STORAGE	149	0	149	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
273	WH-DEL-01	ITM-CBL-01	WH-WH-DEL-01-LOC-ITM-CBL-01-STORAGE	406	0	406	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
274	WH-CCU-01	ITM-CPU-01	WH-WH-CCU-01-LOC-ITM-CPU-01-STORAGE	41	0	41	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
275	WH-CCU-01	ITM-GPU-01	WH-WH-CCU-01-LOC-ITM-GPU-01-STORAGE	32	0	32	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
276	WH-CCU-01	ITM-RAM-01	WH-WH-CCU-01-LOC-ITM-RAM-01-STORAGE	72	0	72	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
277	WH-CCU-01	ITM-SSD-01	WH-WH-CCU-01-LOC-ITM-SSD-01-STORAGE	49	0	49	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
278	WH-CCU-01	ITM-HDD-01	WH-WH-CCU-01-LOC-ITM-HDD-01-STORAGE	81	0	81	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
279	WH-CCU-01	ITM-CHG-01	WH-WH-CCU-01-LOC-ITM-CHG-01-STORAGE	132	0	132	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
280	WH-CCU-01	ITM-CBL-01	WH-WH-CCU-01-LOC-ITM-CBL-01-STORAGE	423	0	423	0	2026-08-19 18:18:37.576137	2026-08-19 18:18:37.576137
\.


--
-- Data for Name: inventory_reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory_reservations (id, order_id, item_id, location_id, reserved_qty, released_qty, created_at) FROM stdin;
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.items (id, name, category, unit_cost, lead_time_days, safety_stock, sku, description, unit, weight_kg, dimensions, barcode, is_active, reorder_threshold, preferred_storage_type, created_at) FROM stdin;
ITM-CPU-01	AMD Ryzen 9 7900X Processor	Electronics	38000	5	15	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.229434
ITM-GPU-01	Nvidia RTX 4080 Founders Edition	Electronics	95000	7	10	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.233436
ITM-RAM-01	Corsair DDR5 32GB 6000MHz RAM	Electronics	8500	4	25	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.237433
ITM-SSD-01	Samsung 990 Pro 2TB NVMe SSD	Storage	12000	3	30	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.241434
ITM-HDD-01	WD Red Pro 8TB NAS Hard Drive	Storage	16500	5	20	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.245435
ITM-CHG-01	Anker 100W GaN Wall Charger	Accessories	2500	2	50	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.248435
ITM-CBL-01	Apple USB-C Braided Cable 2m	Accessories	800	1	100	\N	\N	units	0		\N	t	20	STORAGE	2026-08-19 18:18:37.250433
\.


--
-- Data for Name: notification_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_preferences (id, user_id, category, in_app_enabled, email_enabled, min_severity, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, warehouse_id, event_type, notification_type, title, message, severity, status, channel, source_entity_type, source_entity_id, created_at, read_at, delivered_at, failed_at, retry_count, expires_at, metadata, idempotency_key) FROM stdin;
1	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 15:43:39.785825	\N	2026-08-19 15:43:39.808816	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787134419.785825
2	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 15:43:39.785825	\N	2026-08-19 15:43:39.832833	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787134419.785825
4	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_viewer logged in successfully.	INFO	DELIVERED	IN_APP	USER	4	2026-08-19 15:44:20.732712	\N	2026-08-19 15:44:20.760714	\N	0	\N	{"username": "test_viewer", "message": "User test_viewer logged in successfully."}	USER_LOGIN_4_2_1787134460.732712
5	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_viewer logged in successfully.	INFO	DELIVERED	IN_APP	USER	4	2026-08-19 15:44:20.732712	\N	2026-08-19 15:44:20.790715	\N	0	\N	{"username": "test_viewer", "message": "User test_viewer logged in successfully."}	USER_LOGIN_4_5_1787134460.732712
7	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 15:56:47.633668	\N	2026-08-19 15:56:47.660216	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787135207.633668
8	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 15:56:47.633668	\N	2026-08-19 15:56:47.677739	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787135207.633668
10	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:13:00.712566	\N	2026-08-19 16:13:00.749099	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787136180.712566
11	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:13:00.712566	\N	2026-08-19 16:13:00.767109	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787136180.712566
13	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:19:21.719564	\N	2026-08-19 16:19:21.747653	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787136561.719564
14	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:19:21.719564	\N	2026-08-19 16:19:21.782911	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787136561.719564
16	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:27:27.188078	\N	2026-08-19 16:27:27.197076	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787137047.188078
17	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:27:27.188078	\N	2026-08-19 16:27:27.291971	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787137047.188078
3	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 15:43:39.785825	2026-08-19 16:27:31.703248	2026-08-19 15:43:39.856011	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787134419.785825
6	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_viewer logged in successfully.	INFO	READ	IN_APP	USER	4	2026-08-19 15:44:20.732712	2026-08-19 16:27:31.703248	2026-08-19 15:44:20.820721	\N	0	\N	{"username": "test_viewer", "message": "User test_viewer logged in successfully."}	USER_LOGIN_4_1_1787134460.732712
9	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 15:56:47.633668	2026-08-19 16:27:31.703248	2026-08-19 15:56:47.69074	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787135207.633668
12	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 16:13:00.712566	2026-08-19 16:27:31.703248	2026-08-19 16:13:00.791698	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787136180.712566
15	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 16:19:21.719564	2026-08-19 16:27:31.703248	2026-08-19 16:19:21.79548	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787136561.719564
18	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 16:27:27.188078	2026-08-19 16:27:31.703248	2026-08-19 16:27:27.51398	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787137047.188078
22	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:39:22.825325	\N	2026-08-19 16:39:22.835561	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787137762.825325
23	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 16:39:22.825325	\N	2026-08-19 16:39:22.847571	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787137762.825325
24	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	READ	IN_APP	USER	1	2026-08-19 16:39:22.825325	2026-08-19 16:39:28.135832	2026-08-19 16:39:22.860681	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787137762.825325
25	2	\N	NEW_USER_CREATED	SECURITY_ALERT	New User Created Alert	System event 'New User Account Created' processed successfully.	WARNING	DELIVERED	IN_APP	\N	\N	2026-08-19 16:56:00.032999	\N	2026-08-19 16:56:00.048445	\N	0	\N	{"new_user": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "authorized_by": "admin", "time": "2026-08-19", "message": "System event 'New User Account Created' processed successfully."}	NEW_USER_CREATED_sys_2_1787138760.032999
26	5	\N	NEW_USER_CREATED	SECURITY_ALERT	New User Created Alert	System event 'New User Account Created' processed successfully.	WARNING	DELIVERED	IN_APP	\N	\N	2026-08-19 16:56:00.032999	\N	2026-08-19 16:56:00.063234	\N	0	\N	{"new_user": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "authorized_by": "admin", "time": "2026-08-19", "message": "System event 'New User Account Created' processed successfully."}	NEW_USER_CREATED_sys_5_1787138760.032999
27	1	\N	NEW_USER_CREATED	SECURITY_ALERT	New User Created Alert	System event 'New User Account Created' processed successfully.	WARNING	DELIVERED	IN_APP	\N	\N	2026-08-19 16:56:00.032999	\N	2026-08-19 16:56:00.087227	\N	0	\N	{"new_user": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "authorized_by": "admin", "time": "2026-08-19", "message": "System event 'New User Account Created' processed successfully."}	NEW_USER_CREATED_sys_1_1787138760.032999
28	6	\N	NEW_USER_CREATED	SECURITY_ALERT	New User Created Alert	System event 'New User Account Created' processed successfully.	WARNING	DELIVERED	IN_APP	\N	\N	2026-08-19 16:56:00.032999	\N	2026-08-19 16:56:00.104233	\N	0	\N	{"new_user": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "authorized_by": "admin", "time": "2026-08-19", "message": "System event 'New User Account Created' processed successfully."}	NEW_USER_CREATED_sys_6_1787138760.032999
29	6	\N	NEW_USER_CREATED	SECURITY_ALERT	New User Created Alert	System event 'New User Account Created' processed successfully.	WARNING	SENT	EMAIL	\N	\N	2026-08-19 16:56:00.032999	\N	2026-08-19 16:56:05.620228	\N	0	\N	{"new_user": "harsha200797@gmail.com", "role": "admin", "full_name": "harshavardhan", "authorized_by": "admin", "time": "2026-08-19", "message": "System event 'New User Account Created' processed successfully."}	email_NEW_USER_CREATED_sys_6_1787138760.032999
30	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:12:19.890426	\N	2026-08-19 18:12:19.909441	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787143339.890426
31	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:12:19.890426	\N	2026-08-19 18:12:19.942118	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787143339.890426
32	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:12:19.890426	\N	2026-08-19 18:12:19.966123	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_6_1787143339.890426
34	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:12:19.890426	\N	2026-08-19 18:12:20.023486	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787143339.890426
33	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	SENT	EMAIL	USER	1	2026-08-19 18:12:19.890426	\N	2026-08-19 18:12:25.225442	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	email_USER_LOGIN_1_6_1787143339.890426
35	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:17:29.38003	\N	2026-08-19 18:17:29.390855	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_2_1787143649.38003
36	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:17:29.38003	\N	2026-08-19 18:17:29.39987	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_5_1787143649.38003
37	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:17:29.38003	\N	2026-08-19 18:17:29.412091	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_6_1787143649.38003
39	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	DELIVERED	IN_APP	USER	1	2026-08-19 18:17:29.38003	\N	2026-08-19 18:17:29.438365	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	USER_LOGIN_1_1_1787143649.38003
38	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User admin logged in successfully.	INFO	SENT	EMAIL	USER	1	2026-08-19 18:17:29.38003	\N	2026-08-19 18:17:34.676585	\N	0	\N	{"username": "admin", "message": "User admin logged in successfully."}	email_USER_LOGIN_1_6_1787143649.38003
40	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:18:42.483307	\N	2026-08-19 18:18:42.491631	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_2_1787143722.483307
41	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:18:42.483307	\N	2026-08-19 18:18:42.498633	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_6_1787143722.483307
43	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:18:42.483307	\N	2026-08-19 18:18:42.51963	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_1_1787143722.483307
44	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	DELIVERED	IN_APP	USER	5	2026-08-19 18:18:42.483307	\N	2026-08-19 18:18:42.527641	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	USER_LOGIN_5_5_1787143722.483307
42	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_admin_hardened logged in successfully.	INFO	SENT	EMAIL	USER	5	2026-08-19 18:18:42.483307	\N	2026-08-19 18:18:47.277343	\N	0	\N	{"username": "test_admin_hardened", "message": "User test_admin_hardened logged in successfully."}	email_USER_LOGIN_5_6_1787143722.483307
45	2	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_ai_manager logged in successfully.	INFO	DELIVERED	IN_APP	USER	7	2026-08-19 18:19:19.470316	\N	2026-08-19 18:19:19.476309	\N	0	\N	{"username": "test_ai_manager", "message": "User test_ai_manager logged in successfully."}	USER_LOGIN_7_2_1787143759.470316
46	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_ai_manager logged in successfully.	INFO	DELIVERED	IN_APP	USER	7	2026-08-19 18:19:19.470316	\N	2026-08-19 18:19:19.482307	\N	0	\N	{"username": "test_ai_manager", "message": "User test_ai_manager logged in successfully."}	USER_LOGIN_7_6_1787143759.470316
47	6	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_ai_manager logged in successfully.	INFO	QUEUED	EMAIL	USER	7	2026-08-19 18:19:19.470316	\N	\N	\N	0	\N	{"username": "test_ai_manager", "message": "User test_ai_manager logged in successfully."}	email_USER_LOGIN_7_6_1787143759.470316
48	1	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_ai_manager logged in successfully.	INFO	DELIVERED	IN_APP	USER	7	2026-08-19 18:19:19.470316	\N	2026-08-19 18:19:19.494308	\N	0	\N	{"username": "test_ai_manager", "message": "User test_ai_manager logged in successfully."}	USER_LOGIN_7_1_1787143759.470316
49	5	\N	USER_LOGIN	SECURITY_ALERT	User Login Alert	User test_ai_manager logged in successfully.	INFO	DELIVERED	IN_APP	USER	7	2026-08-19 18:19:19.470316	\N	2026-08-19 18:19:19.499307	\N	0	\N	{"username": "test_ai_manager", "message": "User test_ai_manager logged in successfully."}	USER_LOGIN_7_5_1787143759.470316
\.


--
-- Data for Name: order_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_events (id, order_id, "timestamp", status, event_type, operator, notes) FROM stdin;
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, item_id, requested_qty, reserved_qty, picked_qty, packed_qty, shipped_qty, status) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, customer_ref, warehouse_id, created_at, updated_at, status, priority, total_items, notes, created_by) FROM stdin;
\.


--
-- Data for Name: otp_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otp_records (id, user_id, purpose, code_hash, expires_at, attempts, max_attempts, consumed_at, created_at, request_ip, context_data) FROM stdin;
1	1	ADMIN_CREATION	$2b$12$3xqRDMhLeoAerRIDkUlr5OzzABgRkrLPjfZCKGTPj3edBn/wUBsui	2026-08-19 17:04:52.461116	2	5	2026-08-19 16:55:59.972851	2026-08-19 16:54:52.461116	127.0.0.1	{"target_email": "harsha200797@gmail.com", "full_name": "harshavardhan", "target_role": "admin"}
\.


--
-- Data for Name: packing_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.packing_records (id, order_id, status, started_at, completed_at, operator, package_count, weight_kg, notes) FROM stdin;
\.


--
-- Data for Name: recovery_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recovery_codes (id, user_id, code_hash, used, created_at, used_at) FROM stdin;
\.


--
-- Data for Name: recovery_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recovery_credentials (id, user_id, password_hash, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: robot_reservations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_reservations (id, robot_id, warehouse_id, x, y, tick) FROM stdin;
\.


--
-- Data for Name: robot_routes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_routes (id, robot_id, task_id, warehouse_id, start_x, start_y, goal_x, goal_y, algorithm, path_data, distance, cost, status, created_at, completed_at) FROM stdin;
\.


--
-- Data for Name: robot_telemetry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robot_telemetry (id, robot_id, event_type, "timestamp", x, y, battery, status, task_id, metadata) FROM stdin;
\.


--
-- Data for Name: robots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.robots (id, robot_code, name, warehouse_id, status, battery_level, current_location_id, current_x, current_y, target_location_id, target_x, target_y, assigned_task_id, total_tasks_completed, total_distance, total_operating_time, utilization_percent, failure_count, created_at, updated_at, last_heartbeat_at, robot_type, max_payload, max_speed, enabled, metadata) FROM stdin;
52	RB-BLR-03	Bangalore AGV 03	WH-BLR-01	IDLE	92.5	WH-WH-BLR-01-RECEIVING	1	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
53	RB-CHN-01	Chennai AGV 01	WH-CHN-01	CHARGING	100	WH-WH-CHN-01-CHARGING-1	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
54	RB-BOM-01	Mumbai AGV 01	WH-BOM-01	CHARGING	100	WH-WH-BOM-01-CHARGING-1	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
55	RB-DEL-01	Delhi AGV 01	WH-DEL-01	CHARGING	100	WH-WH-DEL-01-CHARGING-1	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
56	RB-CCU-01	Kolkata AGV 01	WH-CCU-01	CHARGING	100	WH-WH-CCU-01-CHARGING-1	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
50	RB-BLR-01	Bangalore AGV 01	WH-BLR-01	CHARGING	100	WH-WH-BLR-01-CHARGING-1	11	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
51	RB-BLR-02	Bangalore AGV 02	WH-BLR-01	CHARGING	100	WH-WH-BLR-01-CHARGING-2	12	5	\N	0	0	\N	0	0	0	0	0	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	2026-08-19 18:18:37.590639	AGV	200	1.5	t	{}
\.


--
-- Data for Name: scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scenarios (id, name, description, warehouse_id, scenario_type, configuration, random_seed, status, tags, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: shipments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipments (id, order_id, status, tracking_reference, carrier, created_at, shipped_at, delivered_at) FROM stdin;
\.


--
-- Data for Name: shrinkage_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shrinkage_flags (id, date, warehouse_id, item_id, item_name, deviation_score, expected_quantity, actual_quantity, discrepancy_quantity, estimated_exposure, severity, likely_cause, explanation) FROM stdin;
15	2026-08-05	WH-BLR-01	ITM-GPU-01	Nvidia RTX 4080 Founders Edition	0.85	15	5	-10	950000	CRITICAL	UNUSUAL_OUTBOUND_ACTIVITY	Sudden unrecorded drop of 10 units (Valued at ₹9,50,000) occurred outside regular stock-out operations.
16	2026-07-25	WH-CHN-01	ITM-CPU-01	AMD Ryzen 9 7900X Processor	0.72	20	5	-15	570000	HIGH	POSSIBLE_DAMAGE_OR_WASTAGE	Discrepancy of 15 units (Valued at ₹5,70,000) reported at the dock. Unrecorded scraping suspected.
\.


--
-- Data for Name: simulation_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_events (id, simulation_id, warehouse_id, event_type, severity, sim_time_seconds, real_timestamp, robot_id, task_id, location_id, route_id, message, metadata) FROM stdin;
\.


--
-- Data for Name: simulation_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_snapshots (id, simulation_id, warehouse_id, snapshot_version, taken_at, sim_time_seconds, robot_states, task_states, obstacle_states, sim_inventory_delta, metadata) FROM stdin;
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_movements (id, date, warehouse_id, item_id, stock_in, stock_out, closing_stock, is_anomaly, anomaly_type, entry_source, entered_by) FROM stdin;
7351	2026-07-13	WH-BLR-01	ITM-CPU-01	0	1	44	f	none	simulated	system_sim
7352	2026-07-13	WH-BLR-01	ITM-GPU-01	0	1	29	f	none	simulated	system_sim
7353	2026-07-13	WH-BLR-01	ITM-RAM-01	0	2	73	f	none	simulated	system_sim
7354	2026-07-13	WH-BLR-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7355	2026-07-13	WH-BLR-01	ITM-HDD-01	0	2	58	f	none	simulated	system_sim
7356	2026-07-13	WH-BLR-01	ITM-CHG-01	0	8	142	f	none	simulated	system_sim
7357	2026-07-13	WH-BLR-01	ITM-CBL-01	0	6	294	f	none	simulated	system_sim
7358	2026-07-13	WH-CHN-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
7359	2026-07-13	WH-CHN-01	ITM-GPU-01	0	1	29	f	none	simulated	system_sim
7360	2026-07-13	WH-CHN-01	ITM-RAM-01	0	2	73	f	none	simulated	system_sim
7361	2026-07-13	WH-CHN-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7362	2026-07-13	WH-CHN-01	ITM-HDD-01	0	2	58	f	none	simulated	system_sim
7363	2026-07-13	WH-CHN-01	ITM-CHG-01	0	1	149	f	none	simulated	system_sim
7364	2026-07-13	WH-CHN-01	ITM-CBL-01	0	7	293	f	none	simulated	system_sim
7365	2026-07-13	WH-BOM-01	ITM-CPU-01	0	1	44	f	none	simulated	system_sim
7366	2026-07-13	WH-BOM-01	ITM-GPU-01	0	2	28	f	none	simulated	system_sim
7367	2026-07-13	WH-BOM-01	ITM-RAM-01	0	6	69	f	none	simulated	system_sim
7368	2026-07-13	WH-BOM-01	ITM-SSD-01	0	1	89	f	none	simulated	system_sim
7369	2026-07-13	WH-BOM-01	ITM-HDD-01	0	0	60	f	none	simulated	system_sim
7370	2026-07-13	WH-BOM-01	ITM-CHG-01	0	4	146	f	none	simulated	system_sim
7371	2026-07-13	WH-BOM-01	ITM-CBL-01	0	2	298	f	none	simulated	system_sim
7372	2026-07-13	WH-DEL-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
7373	2026-07-13	WH-DEL-01	ITM-GPU-01	0	0	30	f	none	simulated	system_sim
7374	2026-07-13	WH-DEL-01	ITM-RAM-01	0	5	70	f	none	simulated	system_sim
7375	2026-07-13	WH-DEL-01	ITM-SSD-01	0	1	89	f	none	simulated	system_sim
7376	2026-07-13	WH-DEL-01	ITM-HDD-01	0	2	58	f	none	simulated	system_sim
7377	2026-07-13	WH-DEL-01	ITM-CHG-01	0	7	143	f	none	simulated	system_sim
7378	2026-07-13	WH-DEL-01	ITM-CBL-01	0	7	293	f	none	simulated	system_sim
7379	2026-07-13	WH-CCU-01	ITM-CPU-01	0	1	44	f	none	simulated	system_sim
7380	2026-07-13	WH-CCU-01	ITM-GPU-01	0	2	28	f	none	simulated	system_sim
7381	2026-07-13	WH-CCU-01	ITM-RAM-01	0	6	69	f	none	simulated	system_sim
7382	2026-07-13	WH-CCU-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7383	2026-07-13	WH-CCU-01	ITM-HDD-01	0	3	57	f	none	simulated	system_sim
7384	2026-07-13	WH-CCU-01	ITM-CHG-01	0	4	146	f	none	simulated	system_sim
7385	2026-07-13	WH-CCU-01	ITM-CBL-01	0	2	298	f	none	simulated	system_sim
7386	2026-07-14	WH-BLR-01	ITM-CPU-01	0	0	44	f	none	simulated	system_sim
7387	2026-07-14	WH-BLR-01	ITM-GPU-01	0	0	29	f	none	simulated	system_sim
7388	2026-07-14	WH-BLR-01	ITM-RAM-01	0	4	69	f	none	simulated	system_sim
7389	2026-07-14	WH-BLR-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7390	2026-07-14	WH-BLR-01	ITM-HDD-01	0	0	58	f	none	simulated	system_sim
7391	2026-07-14	WH-BLR-01	ITM-CHG-01	0	1	141	f	none	simulated	system_sim
7392	2026-07-14	WH-BLR-01	ITM-CBL-01	0	1	293	f	none	simulated	system_sim
7393	2026-07-14	WH-CHN-01	ITM-CPU-01	0	2	43	f	none	simulated	system_sim
7394	2026-07-14	WH-CHN-01	ITM-GPU-01	0	0	29	f	none	simulated	system_sim
7395	2026-07-14	WH-CHN-01	ITM-RAM-01	0	9	64	f	none	simulated	system_sim
7396	2026-07-14	WH-CHN-01	ITM-SSD-01	0	3	87	f	none	simulated	system_sim
7397	2026-07-14	WH-CHN-01	ITM-HDD-01	0	3	55	f	none	simulated	system_sim
7398	2026-07-14	WH-CHN-01	ITM-CHG-01	0	4	145	f	none	simulated	system_sim
7399	2026-07-14	WH-CHN-01	ITM-CBL-01	0	4	289	f	none	simulated	system_sim
7400	2026-07-14	WH-BOM-01	ITM-CPU-01	0	1	43	f	none	simulated	system_sim
7401	2026-07-14	WH-BOM-01	ITM-GPU-01	0	1	27	f	none	simulated	system_sim
7402	2026-07-14	WH-BOM-01	ITM-RAM-01	0	10	59	f	none	simulated	system_sim
7403	2026-07-14	WH-BOM-01	ITM-SSD-01	0	0	89	f	none	simulated	system_sim
7404	2026-07-14	WH-BOM-01	ITM-HDD-01	0	0	60	f	none	simulated	system_sim
7405	2026-07-14	WH-BOM-01	ITM-CHG-01	0	5	141	f	none	simulated	system_sim
7406	2026-07-14	WH-BOM-01	ITM-CBL-01	0	2	296	f	none	simulated	system_sim
7407	2026-07-14	WH-DEL-01	ITM-CPU-01	0	0	45	f	none	simulated	system_sim
7408	2026-07-14	WH-DEL-01	ITM-GPU-01	0	1	29	f	none	simulated	system_sim
7409	2026-07-14	WH-DEL-01	ITM-RAM-01	0	6	64	f	none	simulated	system_sim
7410	2026-07-14	WH-DEL-01	ITM-SSD-01	0	0	89	f	none	simulated	system_sim
7411	2026-07-14	WH-DEL-01	ITM-HDD-01	0	0	58	f	none	simulated	system_sim
7412	2026-07-14	WH-DEL-01	ITM-CHG-01	0	2	141	f	none	simulated	system_sim
7413	2026-07-14	WH-DEL-01	ITM-CBL-01	0	9	284	f	none	simulated	system_sim
7414	2026-07-14	WH-CCU-01	ITM-CPU-01	0	0	44	f	none	simulated	system_sim
7415	2026-07-14	WH-CCU-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
7416	2026-07-14	WH-CCU-01	ITM-RAM-01	0	3	66	f	none	simulated	system_sim
7417	2026-07-14	WH-CCU-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7418	2026-07-14	WH-CCU-01	ITM-HDD-01	0	2	55	f	none	simulated	system_sim
7419	2026-07-14	WH-CCU-01	ITM-CHG-01	0	4	142	f	none	simulated	system_sim
7420	2026-07-14	WH-CCU-01	ITM-CBL-01	0	9	289	f	none	simulated	system_sim
7421	2026-07-15	WH-BLR-01	ITM-CPU-01	0	2	42	f	none	simulated	system_sim
7422	2026-07-15	WH-BLR-01	ITM-GPU-01	0	2	27	f	none	simulated	system_sim
7423	2026-07-15	WH-BLR-01	ITM-RAM-01	0	5	64	f	none	simulated	system_sim
7424	2026-07-15	WH-BLR-01	ITM-SSD-01	0	0	90	f	none	simulated	system_sim
7425	2026-07-15	WH-BLR-01	ITM-HDD-01	0	0	58	f	none	simulated	system_sim
7426	2026-07-15	WH-BLR-01	ITM-CHG-01	0	10	131	f	none	simulated	system_sim
7427	2026-07-15	WH-BLR-01	ITM-CBL-01	0	7	286	f	none	simulated	system_sim
7428	2026-07-15	WH-CHN-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
7429	2026-07-15	WH-CHN-01	ITM-GPU-01	0	0	29	f	none	simulated	system_sim
7430	2026-07-15	WH-CHN-01	ITM-RAM-01	0	1	63	f	none	simulated	system_sim
7431	2026-07-15	WH-CHN-01	ITM-SSD-01	0	2	85	f	none	simulated	system_sim
7432	2026-07-15	WH-CHN-01	ITM-HDD-01	0	3	52	f	none	simulated	system_sim
7433	2026-07-15	WH-CHN-01	ITM-CHG-01	0	5	140	f	none	simulated	system_sim
7434	2026-07-15	WH-CHN-01	ITM-CBL-01	0	6	283	f	none	simulated	system_sim
7435	2026-07-15	WH-BOM-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
7436	2026-07-15	WH-BOM-01	ITM-GPU-01	0	2	25	f	none	simulated	system_sim
7437	2026-07-15	WH-BOM-01	ITM-RAM-01	0	2	57	f	none	simulated	system_sim
7438	2026-07-15	WH-BOM-01	ITM-SSD-01	0	1	88	f	none	simulated	system_sim
7439	2026-07-15	WH-BOM-01	ITM-HDD-01	0	3	57	f	none	simulated	system_sim
7440	2026-07-15	WH-BOM-01	ITM-CHG-01	0	3	138	f	none	simulated	system_sim
7441	2026-07-15	WH-BOM-01	ITM-CBL-01	0	5	291	f	none	simulated	system_sim
7442	2026-07-15	WH-DEL-01	ITM-CPU-01	0	3	42	f	none	simulated	system_sim
7443	2026-07-15	WH-DEL-01	ITM-GPU-01	0	0	29	f	none	simulated	system_sim
7444	2026-07-15	WH-DEL-01	ITM-RAM-01	0	9	55	f	none	simulated	system_sim
7445	2026-07-15	WH-DEL-01	ITM-SSD-01	0	2	87	f	none	simulated	system_sim
7446	2026-07-15	WH-DEL-01	ITM-HDD-01	0	3	55	f	none	simulated	system_sim
7447	2026-07-15	WH-DEL-01	ITM-CHG-01	0	8	133	f	none	simulated	system_sim
7448	2026-07-15	WH-DEL-01	ITM-CBL-01	0	10	274	f	none	simulated	system_sim
7449	2026-07-15	WH-CCU-01	ITM-CPU-01	0	1	43	f	none	simulated	system_sim
7450	2026-07-15	WH-CCU-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
7451	2026-07-15	WH-CCU-01	ITM-RAM-01	0	2	64	f	none	simulated	system_sim
7452	2026-07-15	WH-CCU-01	ITM-SSD-01	0	3	87	f	none	simulated	system_sim
7453	2026-07-15	WH-CCU-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
7454	2026-07-15	WH-CCU-01	ITM-CHG-01	0	8	134	f	none	simulated	system_sim
7455	2026-07-15	WH-CCU-01	ITM-CBL-01	0	5	284	f	none	simulated	system_sim
7456	2026-07-16	WH-BLR-01	ITM-CPU-01	0	3	39	f	none	simulated	system_sim
7457	2026-07-16	WH-BLR-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
7458	2026-07-16	WH-BLR-01	ITM-RAM-01	0	10	54	f	none	simulated	system_sim
7459	2026-07-16	WH-BLR-01	ITM-SSD-01	0	2	88	f	none	simulated	system_sim
7460	2026-07-16	WH-BLR-01	ITM-HDD-01	0	1	57	f	none	simulated	system_sim
7461	2026-07-16	WH-BLR-01	ITM-CHG-01	0	6	125	f	none	simulated	system_sim
7462	2026-07-16	WH-BLR-01	ITM-CBL-01	0	1	285	f	none	simulated	system_sim
7463	2026-07-16	WH-CHN-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
7464	2026-07-16	WH-CHN-01	ITM-GPU-01	0	1	28	f	none	simulated	system_sim
7465	2026-07-16	WH-CHN-01	ITM-RAM-01	0	2	61	f	none	simulated	system_sim
7466	2026-07-16	WH-CHN-01	ITM-SSD-01	0	1	84	f	none	simulated	system_sim
7467	2026-07-16	WH-CHN-01	ITM-HDD-01	0	2	50	f	none	simulated	system_sim
7468	2026-07-16	WH-CHN-01	ITM-CHG-01	0	9	131	f	none	simulated	system_sim
7469	2026-07-16	WH-CHN-01	ITM-CBL-01	0	9	274	f	none	simulated	system_sim
7470	2026-07-16	WH-BOM-01	ITM-CPU-01	0	3	40	f	none	simulated	system_sim
7471	2026-07-16	WH-BOM-01	ITM-GPU-01	0	2	23	f	none	simulated	system_sim
7472	2026-07-16	WH-BOM-01	ITM-RAM-01	0	7	50	f	none	simulated	system_sim
7473	2026-07-16	WH-BOM-01	ITM-SSD-01	0	3	85	f	none	simulated	system_sim
7474	2026-07-16	WH-BOM-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
7475	2026-07-16	WH-BOM-01	ITM-CHG-01	0	7	131	f	none	simulated	system_sim
7476	2026-07-16	WH-BOM-01	ITM-CBL-01	0	4	287	f	none	simulated	system_sim
7477	2026-07-16	WH-DEL-01	ITM-CPU-01	0	2	40	f	none	simulated	system_sim
7478	2026-07-16	WH-DEL-01	ITM-GPU-01	0	2	27	f	none	simulated	system_sim
7479	2026-07-16	WH-DEL-01	ITM-RAM-01	0	9	46	f	none	simulated	system_sim
7480	2026-07-16	WH-DEL-01	ITM-SSD-01	0	2	85	f	none	simulated	system_sim
7481	2026-07-16	WH-DEL-01	ITM-HDD-01	0	3	52	f	none	simulated	system_sim
7482	2026-07-16	WH-DEL-01	ITM-CHG-01	0	4	129	f	none	simulated	system_sim
7483	2026-07-16	WH-DEL-01	ITM-CBL-01	0	3	271	f	none	simulated	system_sim
7484	2026-07-16	WH-CCU-01	ITM-CPU-01	0	2	41	f	none	simulated	system_sim
7485	2026-07-16	WH-CCU-01	ITM-GPU-01	0	2	26	f	none	simulated	system_sim
7486	2026-07-16	WH-CCU-01	ITM-RAM-01	0	10	54	f	none	simulated	system_sim
7487	2026-07-16	WH-CCU-01	ITM-SSD-01	0	0	87	f	none	simulated	system_sim
7488	2026-07-16	WH-CCU-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
7489	2026-07-16	WH-CCU-01	ITM-CHG-01	0	6	128	f	none	simulated	system_sim
7490	2026-07-16	WH-CCU-01	ITM-CBL-01	0	7	277	f	none	simulated	system_sim
7491	2026-07-17	WH-BLR-01	ITM-CPU-01	0	3	36	f	none	simulated	system_sim
7492	2026-07-17	WH-BLR-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
7493	2026-07-17	WH-BLR-01	ITM-RAM-01	0	7	47	f	none	simulated	system_sim
7494	2026-07-17	WH-BLR-01	ITM-SSD-01	0	2	86	f	none	simulated	system_sim
7495	2026-07-17	WH-BLR-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
7496	2026-07-17	WH-BLR-01	ITM-CHG-01	0	1	124	f	none	simulated	system_sim
7497	2026-07-17	WH-BLR-01	ITM-CBL-01	0	7	278	f	none	simulated	system_sim
7498	2026-07-17	WH-CHN-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
7499	2026-07-17	WH-CHN-01	ITM-GPU-01	0	0	28	f	none	simulated	system_sim
7500	2026-07-17	WH-CHN-01	ITM-RAM-01	0	1	60	f	none	simulated	system_sim
7501	2026-07-17	WH-CHN-01	ITM-SSD-01	0	1	83	f	none	simulated	system_sim
7502	2026-07-17	WH-CHN-01	ITM-HDD-01	0	0	50	f	none	simulated	system_sim
7503	2026-07-17	WH-CHN-01	ITM-CHG-01	0	8	123	f	none	simulated	system_sim
7504	2026-07-17	WH-CHN-01	ITM-CBL-01	0	10	264	f	none	simulated	system_sim
7505	2026-07-17	WH-BOM-01	ITM-CPU-01	0	2	38	f	none	simulated	system_sim
7506	2026-07-17	WH-BOM-01	ITM-GPU-01	0	0	23	f	none	simulated	system_sim
7507	2026-07-17	WH-BOM-01	ITM-RAM-01	0	6	44	f	none	simulated	system_sim
7508	2026-07-17	WH-BOM-01	ITM-SSD-01	0	2	83	f	none	simulated	system_sim
7509	2026-07-17	WH-BOM-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
7510	2026-07-17	WH-BOM-01	ITM-CHG-01	0	4	127	f	none	simulated	system_sim
7511	2026-07-17	WH-BOM-01	ITM-CBL-01	0	7	280	f	none	simulated	system_sim
7512	2026-07-17	WH-DEL-01	ITM-CPU-01	0	3	37	f	none	simulated	system_sim
7513	2026-07-17	WH-DEL-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
7514	2026-07-17	WH-DEL-01	ITM-RAM-01	0	5	41	f	none	simulated	system_sim
7515	2026-07-17	WH-DEL-01	ITM-SSD-01	0	3	82	f	none	simulated	system_sim
7516	2026-07-17	WH-DEL-01	ITM-HDD-01	0	0	52	f	none	simulated	system_sim
7517	2026-07-17	WH-DEL-01	ITM-CHG-01	0	9	120	f	none	simulated	system_sim
7518	2026-07-17	WH-DEL-01	ITM-CBL-01	0	5	266	f	none	simulated	system_sim
7519	2026-07-17	WH-CCU-01	ITM-CPU-01	0	0	41	f	none	simulated	system_sim
7520	2026-07-17	WH-CCU-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
7521	2026-07-17	WH-CCU-01	ITM-RAM-01	0	4	50	f	none	simulated	system_sim
7522	2026-07-17	WH-CCU-01	ITM-SSD-01	0	0	87	f	none	simulated	system_sim
7523	2026-07-17	WH-CCU-01	ITM-HDD-01	0	3	52	f	none	simulated	system_sim
7524	2026-07-17	WH-CCU-01	ITM-CHG-01	0	1	127	f	none	simulated	system_sim
7525	2026-07-17	WH-CCU-01	ITM-CBL-01	0	4	273	f	none	simulated	system_sim
7526	2026-07-18	WH-BLR-01	ITM-CPU-01	0	3	33	f	none	simulated	system_sim
7527	2026-07-18	WH-BLR-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
7528	2026-07-18	WH-BLR-01	ITM-RAM-01	0	4	43	f	none	simulated	system_sim
7529	2026-07-18	WH-BLR-01	ITM-SSD-01	0	0	86	f	none	simulated	system_sim
7530	2026-07-18	WH-BLR-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
7531	2026-07-18	WH-BLR-01	ITM-CHG-01	0	1	123	f	none	simulated	system_sim
7532	2026-07-18	WH-BLR-01	ITM-CBL-01	0	7	271	f	none	simulated	system_sim
7533	2026-07-18	WH-CHN-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
7534	2026-07-18	WH-CHN-01	ITM-GPU-01	0	1	27	f	none	simulated	system_sim
7535	2026-07-18	WH-CHN-01	ITM-RAM-01	0	5	55	f	none	simulated	system_sim
7536	2026-07-18	WH-CHN-01	ITM-SSD-01	0	1	82	f	none	simulated	system_sim
7537	2026-07-18	WH-CHN-01	ITM-HDD-01	0	2	48	f	none	simulated	system_sim
7538	2026-07-18	WH-CHN-01	ITM-CHG-01	0	4	119	f	none	simulated	system_sim
7539	2026-07-18	WH-CHN-01	ITM-CBL-01	0	1	263	f	none	simulated	system_sim
7540	2026-07-18	WH-BOM-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
7541	2026-07-18	WH-BOM-01	ITM-GPU-01	0	1	22	f	none	simulated	system_sim
7542	2026-07-18	WH-BOM-01	ITM-RAM-01	0	2	42	f	none	simulated	system_sim
7543	2026-07-18	WH-BOM-01	ITM-SSD-01	0	1	82	f	none	simulated	system_sim
7544	2026-07-18	WH-BOM-01	ITM-HDD-01	0	0	57	f	none	simulated	system_sim
7545	2026-07-18	WH-BOM-01	ITM-CHG-01	0	1	126	f	none	simulated	system_sim
7546	2026-07-18	WH-BOM-01	ITM-CBL-01	0	10	270	f	none	simulated	system_sim
7547	2026-07-18	WH-DEL-01	ITM-CPU-01	0	3	34	f	none	simulated	system_sim
7548	2026-07-18	WH-DEL-01	ITM-GPU-01	0	0	27	f	none	simulated	system_sim
7549	2026-07-18	WH-DEL-01	ITM-RAM-01	0	7	34	f	none	simulated	system_sim
7550	2026-07-18	WH-DEL-01	ITM-SSD-01	0	0	82	f	none	simulated	system_sim
7551	2026-07-18	WH-DEL-01	ITM-HDD-01	0	3	49	f	none	simulated	system_sim
7552	2026-07-18	WH-DEL-01	ITM-CHG-01	0	6	114	f	none	simulated	system_sim
7553	2026-07-18	WH-DEL-01	ITM-CBL-01	0	6	260	f	none	simulated	system_sim
7554	2026-07-18	WH-CCU-01	ITM-CPU-01	0	0	41	f	none	simulated	system_sim
7555	2026-07-18	WH-CCU-01	ITM-GPU-01	0	2	24	f	none	simulated	system_sim
7556	2026-07-18	WH-CCU-01	ITM-RAM-01	0	4	46	f	none	simulated	system_sim
7557	2026-07-18	WH-CCU-01	ITM-SSD-01	0	3	84	f	none	simulated	system_sim
7558	2026-07-18	WH-CCU-01	ITM-HDD-01	0	1	51	f	none	simulated	system_sim
7559	2026-07-18	WH-CCU-01	ITM-CHG-01	0	4	123	f	none	simulated	system_sim
7560	2026-07-18	WH-CCU-01	ITM-CBL-01	0	9	264	f	none	simulated	system_sim
7561	2026-07-19	WH-BLR-01	ITM-CPU-01	0	1	32	f	none	simulated	system_sim
7562	2026-07-19	WH-BLR-01	ITM-GPU-01	0	1	26	f	none	simulated	system_sim
7563	2026-07-19	WH-BLR-01	ITM-RAM-01	0	4	39	f	none	simulated	system_sim
7564	2026-07-19	WH-BLR-01	ITM-SSD-01	0	0	86	f	none	simulated	system_sim
7565	2026-07-19	WH-BLR-01	ITM-HDD-01	0	2	55	f	none	simulated	system_sim
7566	2026-07-19	WH-BLR-01	ITM-CHG-01	0	1	122	f	none	simulated	system_sim
7567	2026-07-19	WH-BLR-01	ITM-CBL-01	0	2	269	f	none	simulated	system_sim
7568	2026-07-19	WH-CHN-01	ITM-CPU-01	0	3	40	f	none	simulated	system_sim
7569	2026-07-19	WH-CHN-01	ITM-GPU-01	0	1	26	f	none	simulated	system_sim
7570	2026-07-19	WH-CHN-01	ITM-RAM-01	0	2	53	f	none	simulated	system_sim
7571	2026-07-19	WH-CHN-01	ITM-SSD-01	0	3	79	f	none	simulated	system_sim
7572	2026-07-19	WH-CHN-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7573	2026-07-19	WH-CHN-01	ITM-CHG-01	0	10	109	f	none	simulated	system_sim
7574	2026-07-19	WH-CHN-01	ITM-CBL-01	0	7	256	f	none	simulated	system_sim
7575	2026-07-19	WH-BOM-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
7576	2026-07-19	WH-BOM-01	ITM-GPU-01	0	2	20	f	none	simulated	system_sim
7577	2026-07-19	WH-BOM-01	ITM-RAM-01	0	5	37	f	none	simulated	system_sim
7578	2026-07-19	WH-BOM-01	ITM-SSD-01	0	0	82	f	none	simulated	system_sim
7579	2026-07-19	WH-BOM-01	ITM-HDD-01	0	1	56	f	none	simulated	system_sim
7580	2026-07-19	WH-BOM-01	ITM-CHG-01	0	10	116	f	none	simulated	system_sim
7581	2026-07-19	WH-BOM-01	ITM-CBL-01	0	6	264	f	none	simulated	system_sim
7582	2026-07-19	WH-DEL-01	ITM-CPU-01	0	2	32	f	none	simulated	system_sim
7583	2026-07-19	WH-DEL-01	ITM-GPU-01	0	2	25	f	none	simulated	system_sim
7584	2026-07-19	WH-DEL-01	ITM-RAM-01	75	1	108	f	none	simulated	system_sim
7585	2026-07-19	WH-DEL-01	ITM-SSD-01	0	2	80	f	none	simulated	system_sim
7586	2026-07-19	WH-DEL-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
7587	2026-07-19	WH-DEL-01	ITM-CHG-01	0	4	110	f	none	simulated	system_sim
7588	2026-07-19	WH-DEL-01	ITM-CBL-01	0	7	253	f	none	simulated	system_sim
7589	2026-07-19	WH-CCU-01	ITM-CPU-01	0	1	40	f	none	simulated	system_sim
7590	2026-07-19	WH-CCU-01	ITM-GPU-01	0	2	22	f	none	simulated	system_sim
7591	2026-07-19	WH-CCU-01	ITM-RAM-01	0	7	39	f	none	simulated	system_sim
7592	2026-07-19	WH-CCU-01	ITM-SSD-01	0	0	84	f	none	simulated	system_sim
7593	2026-07-19	WH-CCU-01	ITM-HDD-01	0	3	48	f	none	simulated	system_sim
7594	2026-07-19	WH-CCU-01	ITM-CHG-01	0	7	116	f	none	simulated	system_sim
7595	2026-07-19	WH-CCU-01	ITM-CBL-01	0	9	255	f	none	simulated	system_sim
7596	2026-07-20	WH-BLR-01	ITM-CPU-01	0	0	32	f	none	simulated	system_sim
7597	2026-07-20	WH-BLR-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
7598	2026-07-20	WH-BLR-01	ITM-RAM-01	0	4	35	f	none	simulated	system_sim
7599	2026-07-20	WH-BLR-01	ITM-SSD-01	0	1	85	f	none	simulated	system_sim
7600	2026-07-20	WH-BLR-01	ITM-HDD-01	0	0	55	f	none	simulated	system_sim
7601	2026-07-20	WH-BLR-01	ITM-CHG-01	0	6	116	f	none	simulated	system_sim
7602	2026-07-20	WH-BLR-01	ITM-CBL-01	0	8	261	f	none	simulated	system_sim
7603	2026-07-20	WH-CHN-01	ITM-CPU-01	0	3	37	f	none	simulated	system_sim
7604	2026-07-20	WH-CHN-01	ITM-GPU-01	0	1	25	f	none	simulated	system_sim
7605	2026-07-20	WH-CHN-01	ITM-RAM-01	0	7	46	f	none	simulated	system_sim
7606	2026-07-20	WH-CHN-01	ITM-SSD-01	0	0	79	f	none	simulated	system_sim
7607	2026-07-20	WH-CHN-01	ITM-HDD-01	0	3	45	f	none	simulated	system_sim
7608	2026-07-20	WH-CHN-01	ITM-CHG-01	0	4	105	f	none	simulated	system_sim
7609	2026-07-20	WH-CHN-01	ITM-CBL-01	0	10	246	f	none	simulated	system_sim
7610	2026-07-20	WH-BOM-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
7611	2026-07-20	WH-BOM-01	ITM-GPU-01	0	0	20	f	none	simulated	system_sim
7612	2026-07-20	WH-BOM-01	ITM-RAM-01	75	3	109	f	none	simulated	system_sim
7613	2026-07-20	WH-BOM-01	ITM-SSD-01	0	3	79	f	none	simulated	system_sim
7614	2026-07-20	WH-BOM-01	ITM-HDD-01	0	0	56	f	none	simulated	system_sim
7615	2026-07-20	WH-BOM-01	ITM-CHG-01	0	6	110	f	none	simulated	system_sim
7616	2026-07-20	WH-BOM-01	ITM-CBL-01	0	2	262	f	none	simulated	system_sim
7617	2026-07-20	WH-DEL-01	ITM-CPU-01	0	1	31	f	none	simulated	system_sim
7618	2026-07-20	WH-DEL-01	ITM-GPU-01	0	1	24	f	none	simulated	system_sim
7619	2026-07-20	WH-DEL-01	ITM-RAM-01	0	8	100	f	none	simulated	system_sim
7620	2026-07-20	WH-DEL-01	ITM-SSD-01	0	3	77	f	none	simulated	system_sim
7621	2026-07-20	WH-DEL-01	ITM-HDD-01	0	1	48	f	none	simulated	system_sim
7622	2026-07-20	WH-DEL-01	ITM-CHG-01	0	2	108	f	none	simulated	system_sim
7623	2026-07-20	WH-DEL-01	ITM-CBL-01	0	9	244	f	none	simulated	system_sim
7624	2026-07-20	WH-CCU-01	ITM-CPU-01	0	1	39	f	none	simulated	system_sim
7625	2026-07-20	WH-CCU-01	ITM-GPU-01	0	1	21	f	none	simulated	system_sim
7626	2026-07-20	WH-CCU-01	ITM-RAM-01	0	4	35	f	none	simulated	system_sim
7627	2026-07-20	WH-CCU-01	ITM-SSD-01	0	3	81	f	none	simulated	system_sim
7628	2026-07-20	WH-CCU-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7629	2026-07-20	WH-CCU-01	ITM-CHG-01	0	2	114	f	none	simulated	system_sim
7630	2026-07-20	WH-CCU-01	ITM-CBL-01	0	10	245	f	none	simulated	system_sim
7631	2026-07-21	WH-BLR-01	ITM-CPU-01	0	3	29	f	none	simulated	system_sim
7632	2026-07-21	WH-BLR-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
7633	2026-07-21	WH-BLR-01	ITM-RAM-01	75	2	108	f	none	simulated	system_sim
7634	2026-07-21	WH-BLR-01	ITM-SSD-01	0	0	85	f	none	simulated	system_sim
7635	2026-07-21	WH-BLR-01	ITM-HDD-01	0	2	53	f	none	simulated	system_sim
7636	2026-07-21	WH-BLR-01	ITM-CHG-01	0	4	112	f	none	simulated	system_sim
7637	2026-07-21	WH-BLR-01	ITM-CBL-01	0	1	260	f	none	simulated	system_sim
7638	2026-07-21	WH-CHN-01	ITM-CPU-01	0	3	34	f	none	simulated	system_sim
7639	2026-07-21	WH-CHN-01	ITM-GPU-01	0	1	24	f	none	simulated	system_sim
7640	2026-07-21	WH-CHN-01	ITM-RAM-01	0	1	45	f	none	simulated	system_sim
7641	2026-07-21	WH-CHN-01	ITM-SSD-01	0	2	77	f	none	simulated	system_sim
7642	2026-07-21	WH-CHN-01	ITM-HDD-01	0	3	42	f	none	simulated	system_sim
7643	2026-07-21	WH-CHN-01	ITM-CHG-01	0	7	98	f	none	simulated	system_sim
7644	2026-07-21	WH-CHN-01	ITM-CBL-01	0	6	240	f	none	simulated	system_sim
7645	2026-07-21	WH-BOM-01	ITM-CPU-01	0	0	38	f	none	simulated	system_sim
7646	2026-07-21	WH-BOM-01	ITM-GPU-01	0	1	19	f	none	simulated	system_sim
7647	2026-07-21	WH-BOM-01	ITM-RAM-01	0	9	100	f	none	simulated	system_sim
7648	2026-07-21	WH-BOM-01	ITM-SSD-01	0	2	77	f	none	simulated	system_sim
7649	2026-07-21	WH-BOM-01	ITM-HDD-01	0	0	56	f	none	simulated	system_sim
7650	2026-07-21	WH-BOM-01	ITM-CHG-01	0	1	109	f	none	simulated	system_sim
7651	2026-07-21	WH-BOM-01	ITM-CBL-01	0	4	258	f	none	simulated	system_sim
7652	2026-07-21	WH-DEL-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
7653	2026-07-21	WH-DEL-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
7654	2026-07-21	WH-DEL-01	ITM-RAM-01	0	4	96	f	none	simulated	system_sim
7655	2026-07-21	WH-DEL-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
7656	2026-07-21	WH-DEL-01	ITM-HDD-01	0	1	47	f	none	simulated	system_sim
7657	2026-07-21	WH-DEL-01	ITM-CHG-01	0	8	100	f	none	simulated	system_sim
7658	2026-07-21	WH-DEL-01	ITM-CBL-01	0	8	236	f	none	simulated	system_sim
7659	2026-07-21	WH-CCU-01	ITM-CPU-01	0	0	39	f	none	simulated	system_sim
7660	2026-07-21	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
7661	2026-07-21	WH-CCU-01	ITM-RAM-01	75	3	107	f	none	simulated	system_sim
7662	2026-07-21	WH-CCU-01	ITM-SSD-01	0	3	78	f	none	simulated	system_sim
7663	2026-07-21	WH-CCU-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7664	2026-07-21	WH-CCU-01	ITM-CHG-01	0	9	105	f	none	simulated	system_sim
7665	2026-07-21	WH-CCU-01	ITM-CBL-01	0	8	237	f	none	simulated	system_sim
7666	2026-07-22	WH-BLR-01	ITM-CPU-01	0	2	27	f	none	simulated	system_sim
7667	2026-07-22	WH-BLR-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
7668	2026-07-22	WH-BLR-01	ITM-RAM-01	0	3	105	f	none	simulated	system_sim
7669	2026-07-22	WH-BLR-01	ITM-SSD-01	0	2	83	f	none	simulated	system_sim
7670	2026-07-22	WH-BLR-01	ITM-HDD-01	0	1	52	f	none	simulated	system_sim
7671	2026-07-22	WH-BLR-01	ITM-CHG-01	0	9	103	f	none	simulated	system_sim
7672	2026-07-22	WH-BLR-01	ITM-CBL-01	0	2	258	f	none	simulated	system_sim
7673	2026-07-22	WH-CHN-01	ITM-CPU-01	0	0	34	f	none	simulated	system_sim
7674	2026-07-22	WH-CHN-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
7675	2026-07-22	WH-CHN-01	ITM-RAM-01	0	9	36	f	none	simulated	system_sim
7676	2026-07-22	WH-CHN-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
7677	2026-07-22	WH-CHN-01	ITM-HDD-01	0	0	42	f	none	simulated	system_sim
7678	2026-07-22	WH-CHN-01	ITM-CHG-01	0	10	88	f	none	simulated	system_sim
7679	2026-07-22	WH-CHN-01	ITM-CBL-01	0	2	238	f	none	simulated	system_sim
7680	2026-07-22	WH-BOM-01	ITM-CPU-01	0	2	36	f	none	simulated	system_sim
7681	2026-07-22	WH-BOM-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7682	2026-07-22	WH-BOM-01	ITM-RAM-01	0	10	90	f	none	simulated	system_sim
7683	2026-07-22	WH-BOM-01	ITM-SSD-01	0	3	74	f	none	simulated	system_sim
7684	2026-07-22	WH-BOM-01	ITM-HDD-01	0	3	53	f	none	simulated	system_sim
7685	2026-07-22	WH-BOM-01	ITM-CHG-01	0	9	100	f	none	simulated	system_sim
7686	2026-07-22	WH-BOM-01	ITM-CBL-01	0	5	253	f	none	simulated	system_sim
7687	2026-07-22	WH-DEL-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
7688	2026-07-22	WH-DEL-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
7689	2026-07-22	WH-DEL-01	ITM-RAM-01	0	10	86	f	none	simulated	system_sim
7690	2026-07-22	WH-DEL-01	ITM-SSD-01	0	2	75	f	none	simulated	system_sim
7691	2026-07-22	WH-DEL-01	ITM-HDD-01	0	2	45	f	none	simulated	system_sim
7692	2026-07-22	WH-DEL-01	ITM-CHG-01	0	5	95	f	none	simulated	system_sim
7693	2026-07-22	WH-DEL-01	ITM-CBL-01	0	4	232	f	none	simulated	system_sim
7694	2026-07-22	WH-CCU-01	ITM-CPU-01	0	3	36	f	none	simulated	system_sim
7695	2026-07-22	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
7696	2026-07-22	WH-CCU-01	ITM-RAM-01	0	4	103	f	none	simulated	system_sim
7697	2026-07-22	WH-CCU-01	ITM-SSD-01	0	0	78	f	none	simulated	system_sim
7698	2026-07-22	WH-CCU-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7699	2026-07-22	WH-CCU-01	ITM-CHG-01	0	7	98	f	none	simulated	system_sim
7700	2026-07-22	WH-CCU-01	ITM-CBL-01	0	1	236	f	none	simulated	system_sim
7701	2026-07-23	WH-BLR-01	ITM-CPU-01	0	2	25	f	none	simulated	system_sim
7702	2026-07-23	WH-BLR-01	ITM-GPU-01	0	0	26	f	none	simulated	system_sim
7703	2026-07-23	WH-BLR-01	ITM-RAM-01	0	8	97	f	none	simulated	system_sim
7704	2026-07-23	WH-BLR-01	ITM-SSD-01	0	2	81	f	none	simulated	system_sim
7705	2026-07-23	WH-BLR-01	ITM-HDD-01	0	3	49	f	none	simulated	system_sim
7706	2026-07-23	WH-BLR-01	ITM-CHG-01	0	8	95	f	none	simulated	system_sim
7707	2026-07-23	WH-BLR-01	ITM-CBL-01	0	9	249	f	none	simulated	system_sim
7708	2026-07-23	WH-CHN-01	ITM-CPU-01	0	0	34	f	none	simulated	system_sim
7709	2026-07-23	WH-CHN-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
7710	2026-07-23	WH-CHN-01	ITM-RAM-01	75	8	103	f	none	simulated	system_sim
7711	2026-07-23	WH-CHN-01	ITM-SSD-01	0	0	77	f	none	simulated	system_sim
7712	2026-07-23	WH-CHN-01	ITM-HDD-01	0	3	39	f	none	simulated	system_sim
7713	2026-07-23	WH-CHN-01	ITM-CHG-01	0	9	79	f	none	simulated	system_sim
7714	2026-07-23	WH-CHN-01	ITM-CBL-01	0	7	231	f	none	simulated	system_sim
7715	2026-07-23	WH-BOM-01	ITM-CPU-01	0	3	33	f	none	simulated	system_sim
7716	2026-07-23	WH-BOM-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7717	2026-07-23	WH-BOM-01	ITM-RAM-01	0	3	87	f	none	simulated	system_sim
7718	2026-07-23	WH-BOM-01	ITM-SSD-01	0	3	71	f	none	simulated	system_sim
7719	2026-07-23	WH-BOM-01	ITM-HDD-01	0	0	53	f	none	simulated	system_sim
7720	2026-07-23	WH-BOM-01	ITM-CHG-01	0	5	95	f	none	simulated	system_sim
7721	2026-07-23	WH-BOM-01	ITM-CBL-01	0	7	246	f	none	simulated	system_sim
7722	2026-07-23	WH-DEL-01	ITM-CPU-01	0	1	30	f	none	simulated	system_sim
7723	2026-07-23	WH-DEL-01	ITM-GPU-01	0	0	24	f	none	simulated	system_sim
7724	2026-07-23	WH-DEL-01	ITM-RAM-01	0	1	85	f	none	simulated	system_sim
7725	2026-07-23	WH-DEL-01	ITM-SSD-01	0	2	73	f	none	simulated	system_sim
7726	2026-07-23	WH-DEL-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
7727	2026-07-23	WH-DEL-01	ITM-CHG-01	0	1	94	f	none	simulated	system_sim
7728	2026-07-23	WH-DEL-01	ITM-CBL-01	0	7	225	f	none	simulated	system_sim
7729	2026-07-23	WH-CCU-01	ITM-CPU-01	0	0	36	f	none	simulated	system_sim
7730	2026-07-23	WH-CCU-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
7731	2026-07-23	WH-CCU-01	ITM-RAM-01	0	6	97	f	none	simulated	system_sim
7732	2026-07-23	WH-CCU-01	ITM-SSD-01	0	1	77	f	none	simulated	system_sim
7733	2026-07-23	WH-CCU-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7734	2026-07-23	WH-CCU-01	ITM-CHG-01	0	9	89	f	none	simulated	system_sim
7735	2026-07-23	WH-CCU-01	ITM-CBL-01	0	8	228	f	none	simulated	system_sim
7736	2026-07-24	WH-BLR-01	ITM-CPU-01	0	2	23	f	none	simulated	system_sim
7737	2026-07-24	WH-BLR-01	ITM-GPU-01	0	2	24	f	none	simulated	system_sim
7738	2026-07-24	WH-BLR-01	ITM-RAM-01	0	5	92	f	none	simulated	system_sim
7739	2026-07-24	WH-BLR-01	ITM-SSD-01	0	0	81	f	none	simulated	system_sim
7740	2026-07-24	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
7741	2026-07-24	WH-BLR-01	ITM-CHG-01	0	7	88	f	none	simulated	system_sim
7742	2026-07-24	WH-BLR-01	ITM-CBL-01	0	8	241	f	none	simulated	system_sim
7743	2026-07-24	WH-CHN-01	ITM-CPU-01	0	2	32	f	none	simulated	system_sim
7744	2026-07-24	WH-CHN-01	ITM-GPU-01	0	2	22	f	none	simulated	system_sim
7745	2026-07-24	WH-CHN-01	ITM-RAM-01	0	7	96	f	none	simulated	system_sim
7746	2026-07-24	WH-CHN-01	ITM-SSD-01	0	1	76	f	none	simulated	system_sim
7747	2026-07-24	WH-CHN-01	ITM-HDD-01	0	1	38	f	none	simulated	system_sim
7748	2026-07-24	WH-CHN-01	ITM-CHG-01	0	8	71	f	none	simulated	system_sim
7749	2026-07-24	WH-CHN-01	ITM-CBL-01	0	1	230	f	none	simulated	system_sim
7750	2026-07-24	WH-BOM-01	ITM-CPU-01	0	2	31	f	none	simulated	system_sim
7751	2026-07-24	WH-BOM-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7752	2026-07-24	WH-BOM-01	ITM-RAM-01	0	6	81	f	none	simulated	system_sim
7753	2026-07-24	WH-BOM-01	ITM-SSD-01	0	0	71	f	none	simulated	system_sim
7754	2026-07-24	WH-BOM-01	ITM-HDD-01	0	3	50	f	none	simulated	system_sim
7755	2026-07-24	WH-BOM-01	ITM-CHG-01	0	10	85	f	none	simulated	system_sim
7756	2026-07-24	WH-BOM-01	ITM-CBL-01	0	10	236	f	none	simulated	system_sim
7757	2026-07-24	WH-DEL-01	ITM-CPU-01	0	2	28	f	none	simulated	system_sim
7758	2026-07-24	WH-DEL-01	ITM-GPU-01	0	1	23	f	none	simulated	system_sim
7759	2026-07-24	WH-DEL-01	ITM-RAM-01	0	8	77	f	none	simulated	system_sim
7760	2026-07-24	WH-DEL-01	ITM-SSD-01	0	0	73	f	none	simulated	system_sim
7761	2026-07-24	WH-DEL-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
7762	2026-07-24	WH-DEL-01	ITM-CHG-01	0	3	91	f	none	simulated	system_sim
7763	2026-07-24	WH-DEL-01	ITM-CBL-01	0	6	219	f	none	simulated	system_sim
7764	2026-07-24	WH-CCU-01	ITM-CPU-01	0	3	33	f	none	simulated	system_sim
7765	2026-07-24	WH-CCU-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
7766	2026-07-24	WH-CCU-01	ITM-RAM-01	0	3	94	f	none	simulated	system_sim
7767	2026-07-24	WH-CCU-01	ITM-SSD-01	0	1	76	f	none	simulated	system_sim
7768	2026-07-24	WH-CCU-01	ITM-HDD-01	0	0	48	f	none	simulated	system_sim
7769	2026-07-24	WH-CCU-01	ITM-CHG-01	0	6	83	f	none	simulated	system_sim
7770	2026-07-24	WH-CCU-01	ITM-CBL-01	0	4	224	f	none	simulated	system_sim
7771	2026-07-25	WH-BLR-01	ITM-CPU-01	0	2	21	f	none	simulated	system_sim
7772	2026-07-25	WH-BLR-01	ITM-GPU-01	0	2	22	f	none	simulated	system_sim
7773	2026-07-25	WH-BLR-01	ITM-RAM-01	0	10	82	f	none	simulated	system_sim
7774	2026-07-25	WH-BLR-01	ITM-SSD-01	0	3	78	f	none	simulated	system_sim
7775	2026-07-25	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
7776	2026-07-25	WH-BLR-01	ITM-CHG-01	0	9	79	f	none	simulated	system_sim
7777	2026-07-25	WH-BLR-01	ITM-CBL-01	0	2	239	f	none	simulated	system_sim
7778	2026-07-25	WH-CHN-01	ITM-CPU-01	0	1	16	t	shrinkage	simulated	system_sim
7779	2026-07-25	WH-CHN-01	ITM-GPU-01	0	0	22	f	none	simulated	system_sim
7780	2026-07-25	WH-CHN-01	ITM-RAM-01	0	10	86	f	none	simulated	system_sim
7781	2026-07-25	WH-CHN-01	ITM-SSD-01	0	2	74	f	none	simulated	system_sim
7782	2026-07-25	WH-CHN-01	ITM-HDD-01	0	0	38	f	none	simulated	system_sim
7783	2026-07-25	WH-CHN-01	ITM-CHG-01	150	10	211	f	none	simulated	system_sim
7784	2026-07-25	WH-CHN-01	ITM-CBL-01	0	5	225	f	none	simulated	system_sim
7785	2026-07-25	WH-BOM-01	ITM-CPU-01	0	0	31	f	none	simulated	system_sim
7786	2026-07-25	WH-BOM-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7787	2026-07-25	WH-BOM-01	ITM-RAM-01	0	8	73	f	none	simulated	system_sim
7788	2026-07-25	WH-BOM-01	ITM-SSD-01	0	0	71	f	none	simulated	system_sim
7789	2026-07-25	WH-BOM-01	ITM-HDD-01	0	0	50	f	none	simulated	system_sim
7790	2026-07-25	WH-BOM-01	ITM-CHG-01	0	10	75	f	none	simulated	system_sim
7791	2026-07-25	WH-BOM-01	ITM-CBL-01	0	1	235	f	none	simulated	system_sim
7792	2026-07-25	WH-DEL-01	ITM-CPU-01	0	3	25	f	none	simulated	system_sim
7793	2026-07-25	WH-DEL-01	ITM-GPU-01	0	2	21	f	none	simulated	system_sim
7794	2026-07-25	WH-DEL-01	ITM-RAM-01	0	5	72	f	none	simulated	system_sim
7795	2026-07-25	WH-DEL-01	ITM-SSD-01	0	1	72	f	none	simulated	system_sim
7796	2026-07-25	WH-DEL-01	ITM-HDD-01	0	2	43	f	none	simulated	system_sim
7797	2026-07-25	WH-DEL-01	ITM-CHG-01	0	1	90	f	none	simulated	system_sim
7798	2026-07-25	WH-DEL-01	ITM-CBL-01	0	5	214	f	none	simulated	system_sim
7799	2026-07-25	WH-CCU-01	ITM-CPU-01	0	0	33	f	none	simulated	system_sim
7800	2026-07-25	WH-CCU-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7801	2026-07-25	WH-CCU-01	ITM-RAM-01	0	10	84	f	none	simulated	system_sim
7802	2026-07-25	WH-CCU-01	ITM-SSD-01	0	3	73	f	none	simulated	system_sim
7803	2026-07-25	WH-CCU-01	ITM-HDD-01	0	2	46	f	none	simulated	system_sim
7804	2026-07-25	WH-CCU-01	ITM-CHG-01	0	8	75	f	none	simulated	system_sim
7805	2026-07-25	WH-CCU-01	ITM-CBL-01	0	7	217	f	none	simulated	system_sim
7806	2026-07-26	WH-BLR-01	ITM-CPU-01	45	3	63	f	none	simulated	system_sim
7807	2026-07-26	WH-BLR-01	ITM-GPU-01	0	1	21	f	none	simulated	system_sim
7808	2026-07-26	WH-BLR-01	ITM-RAM-01	0	3	79	f	none	simulated	system_sim
7809	2026-07-26	WH-BLR-01	ITM-SSD-01	0	2	76	f	none	simulated	system_sim
7810	2026-07-26	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
7811	2026-07-26	WH-BLR-01	ITM-CHG-01	0	3	76	f	none	simulated	system_sim
7812	2026-07-26	WH-BLR-01	ITM-CBL-01	0	10	229	f	none	simulated	system_sim
7813	2026-07-26	WH-CHN-01	ITM-CPU-01	45	2	59	f	none	simulated	system_sim
7814	2026-07-26	WH-CHN-01	ITM-GPU-01	0	0	22	f	none	simulated	system_sim
7815	2026-07-26	WH-CHN-01	ITM-RAM-01	0	1	85	f	none	simulated	system_sim
7816	2026-07-26	WH-CHN-01	ITM-SSD-01	0	0	74	f	none	simulated	system_sim
7817	2026-07-26	WH-CHN-01	ITM-HDD-01	0	3	35	f	none	simulated	system_sim
7818	2026-07-26	WH-CHN-01	ITM-CHG-01	0	4	207	f	none	simulated	system_sim
7819	2026-07-26	WH-CHN-01	ITM-CBL-01	0	9	216	f	none	simulated	system_sim
7820	2026-07-26	WH-BOM-01	ITM-CPU-01	0	2	29	f	none	simulated	system_sim
7821	2026-07-26	WH-BOM-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7822	2026-07-26	WH-BOM-01	ITM-RAM-01	0	3	70	f	none	simulated	system_sim
7823	2026-07-26	WH-BOM-01	ITM-SSD-01	0	1	70	f	none	simulated	system_sim
7824	2026-07-26	WH-BOM-01	ITM-HDD-01	0	1	49	f	none	simulated	system_sim
7825	2026-07-26	WH-BOM-01	ITM-CHG-01	0	1	74	f	none	simulated	system_sim
7826	2026-07-26	WH-BOM-01	ITM-CBL-01	0	1	234	f	none	simulated	system_sim
7827	2026-07-26	WH-DEL-01	ITM-CPU-01	0	0	25	f	none	simulated	system_sim
7828	2026-07-26	WH-DEL-01	ITM-GPU-01	0	0	21	f	none	simulated	system_sim
7829	2026-07-26	WH-DEL-01	ITM-RAM-01	0	9	63	f	none	simulated	system_sim
7830	2026-07-26	WH-DEL-01	ITM-SSD-01	0	0	72	f	none	simulated	system_sim
7831	2026-07-26	WH-DEL-01	ITM-HDD-01	0	1	42	f	none	simulated	system_sim
7832	2026-07-26	WH-DEL-01	ITM-CHG-01	0	3	87	f	none	simulated	system_sim
7833	2026-07-26	WH-DEL-01	ITM-CBL-01	0	8	206	f	none	simulated	system_sim
7834	2026-07-26	WH-CCU-01	ITM-CPU-01	0	1	32	f	none	simulated	system_sim
7835	2026-07-26	WH-CCU-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
7836	2026-07-26	WH-CCU-01	ITM-RAM-01	0	3	81	f	none	simulated	system_sim
7837	2026-07-26	WH-CCU-01	ITM-SSD-01	0	2	71	f	none	simulated	system_sim
7838	2026-07-26	WH-CCU-01	ITM-HDD-01	0	0	46	f	none	simulated	system_sim
7839	2026-07-26	WH-CCU-01	ITM-CHG-01	0	5	70	f	none	simulated	system_sim
7840	2026-07-26	WH-CCU-01	ITM-CBL-01	0	3	214	f	none	simulated	system_sim
7841	2026-07-27	WH-BLR-01	ITM-CPU-01	0	0	63	f	none	simulated	system_sim
7842	2026-07-27	WH-BLR-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
7843	2026-07-27	WH-BLR-01	ITM-RAM-01	0	5	74	f	none	simulated	system_sim
7844	2026-07-27	WH-BLR-01	ITM-SSD-01	0	3	73	f	none	simulated	system_sim
7845	2026-07-27	WH-BLR-01	ITM-HDD-01	0	0	49	f	none	simulated	system_sim
7846	2026-07-27	WH-BLR-01	ITM-CHG-01	0	6	70	f	none	simulated	system_sim
7847	2026-07-27	WH-BLR-01	ITM-CBL-01	0	2	227	f	none	simulated	system_sim
7848	2026-07-27	WH-CHN-01	ITM-CPU-01	0	0	59	f	none	simulated	system_sim
7849	2026-07-27	WH-CHN-01	ITM-GPU-01	0	1	21	f	none	simulated	system_sim
7850	2026-07-27	WH-CHN-01	ITM-RAM-01	0	10	75	f	none	simulated	system_sim
7851	2026-07-27	WH-CHN-01	ITM-SSD-01	0	3	71	f	none	simulated	system_sim
7852	2026-07-27	WH-CHN-01	ITM-HDD-01	0	1	34	f	none	simulated	system_sim
7853	2026-07-27	WH-CHN-01	ITM-CHG-01	0	8	199	f	none	simulated	system_sim
7854	2026-07-27	WH-CHN-01	ITM-CBL-01	0	5	211	f	none	simulated	system_sim
7855	2026-07-27	WH-BOM-01	ITM-CPU-01	0	2	27	f	none	simulated	system_sim
7856	2026-07-27	WH-BOM-01	ITM-GPU-01	0	2	17	f	none	simulated	system_sim
7857	2026-07-27	WH-BOM-01	ITM-RAM-01	0	2	68	f	none	simulated	system_sim
7858	2026-07-27	WH-BOM-01	ITM-SSD-01	0	2	68	f	none	simulated	system_sim
7859	2026-07-27	WH-BOM-01	ITM-HDD-01	0	3	46	f	none	simulated	system_sim
7860	2026-07-27	WH-BOM-01	ITM-CHG-01	150	10	214	f	none	simulated	system_sim
7861	2026-07-27	WH-BOM-01	ITM-CBL-01	0	3	231	f	none	simulated	system_sim
7862	2026-07-27	WH-DEL-01	ITM-CPU-01	0	3	22	f	none	simulated	system_sim
7863	2026-07-27	WH-DEL-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
7864	2026-07-27	WH-DEL-01	ITM-RAM-01	0	5	58	f	none	simulated	system_sim
7865	2026-07-27	WH-DEL-01	ITM-SSD-01	0	2	70	f	none	simulated	system_sim
7866	2026-07-27	WH-DEL-01	ITM-HDD-01	0	3	39	f	none	simulated	system_sim
7867	2026-07-27	WH-DEL-01	ITM-CHG-01	0	2	85	f	none	simulated	system_sim
7868	2026-07-27	WH-DEL-01	ITM-CBL-01	0	7	199	f	none	simulated	system_sim
7869	2026-07-27	WH-CCU-01	ITM-CPU-01	0	0	32	f	none	simulated	system_sim
7870	2026-07-27	WH-CCU-01	ITM-GPU-01	0	1	17	f	none	simulated	system_sim
7871	2026-07-27	WH-CCU-01	ITM-RAM-01	0	4	77	f	none	simulated	system_sim
7872	2026-07-27	WH-CCU-01	ITM-SSD-01	0	0	71	f	none	simulated	system_sim
7873	2026-07-27	WH-CCU-01	ITM-HDD-01	0	2	44	f	none	simulated	system_sim
7874	2026-07-27	WH-CCU-01	ITM-CHG-01	150	6	214	f	none	simulated	system_sim
7875	2026-07-27	WH-CCU-01	ITM-CBL-01	0	6	208	f	none	simulated	system_sim
7876	2026-07-28	WH-BLR-01	ITM-CPU-01	0	0	63	f	none	simulated	system_sim
7877	2026-07-28	WH-BLR-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
7878	2026-07-28	WH-BLR-01	ITM-RAM-01	0	6	68	f	none	simulated	system_sim
7879	2026-07-28	WH-BLR-01	ITM-SSD-01	0	1	72	f	none	simulated	system_sim
7880	2026-07-28	WH-BLR-01	ITM-HDD-01	0	3	46	f	none	simulated	system_sim
7881	2026-07-28	WH-BLR-01	ITM-CHG-01	150	8	212	f	none	simulated	system_sim
7882	2026-07-28	WH-BLR-01	ITM-CBL-01	0	4	223	f	none	simulated	system_sim
7883	2026-07-28	WH-CHN-01	ITM-CPU-01	0	0	59	f	none	simulated	system_sim
7884	2026-07-28	WH-CHN-01	ITM-GPU-01	0	2	19	f	none	simulated	system_sim
7885	2026-07-28	WH-CHN-01	ITM-RAM-01	0	2	73	f	none	simulated	system_sim
7886	2026-07-28	WH-CHN-01	ITM-SSD-01	0	3	68	f	none	simulated	system_sim
7887	2026-07-28	WH-CHN-01	ITM-HDD-01	0	3	31	f	none	simulated	system_sim
7888	2026-07-28	WH-CHN-01	ITM-CHG-01	0	7	192	f	none	simulated	system_sim
7889	2026-07-28	WH-CHN-01	ITM-CBL-01	0	4	207	f	none	simulated	system_sim
7890	2026-07-28	WH-BOM-01	ITM-CPU-01	0	0	27	f	none	simulated	system_sim
7891	2026-07-28	WH-BOM-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7892	2026-07-28	WH-BOM-01	ITM-RAM-01	0	9	59	f	none	simulated	system_sim
7893	2026-07-28	WH-BOM-01	ITM-SSD-01	0	3	65	f	none	simulated	system_sim
7894	2026-07-28	WH-BOM-01	ITM-HDD-01	0	0	46	f	none	simulated	system_sim
7895	2026-07-28	WH-BOM-01	ITM-CHG-01	0	10	204	f	none	simulated	system_sim
7896	2026-07-28	WH-BOM-01	ITM-CBL-01	0	2	229	f	none	simulated	system_sim
7897	2026-07-28	WH-DEL-01	ITM-CPU-01	45	2	65	f	none	simulated	system_sim
7898	2026-07-28	WH-DEL-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
7899	2026-07-28	WH-DEL-01	ITM-RAM-01	0	3	55	f	none	simulated	system_sim
7900	2026-07-28	WH-DEL-01	ITM-SSD-01	0	1	69	f	none	simulated	system_sim
7901	2026-07-28	WH-DEL-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
7902	2026-07-28	WH-DEL-01	ITM-CHG-01	0	6	79	f	none	simulated	system_sim
7903	2026-07-28	WH-DEL-01	ITM-CBL-01	0	6	193	f	none	simulated	system_sim
7904	2026-07-28	WH-CCU-01	ITM-CPU-01	0	2	30	f	none	simulated	system_sim
7905	2026-07-28	WH-CCU-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7906	2026-07-28	WH-CCU-01	ITM-RAM-01	0	9	68	f	none	simulated	system_sim
7907	2026-07-28	WH-CCU-01	ITM-SSD-01	0	3	68	f	none	simulated	system_sim
7908	2026-07-28	WH-CCU-01	ITM-HDD-01	0	2	42	f	none	simulated	system_sim
7909	2026-07-28	WH-CCU-01	ITM-CHG-01	0	5	209	f	none	simulated	system_sim
7910	2026-07-28	WH-CCU-01	ITM-CBL-01	0	4	204	f	none	simulated	system_sim
7911	2026-07-29	WH-BLR-01	ITM-CPU-01	0	3	60	f	none	simulated	system_sim
7912	2026-07-29	WH-BLR-01	ITM-GPU-01	0	1	17	f	none	simulated	system_sim
7913	2026-07-29	WH-BLR-01	ITM-RAM-01	0	6	62	f	none	simulated	system_sim
7914	2026-07-29	WH-BLR-01	ITM-SSD-01	0	0	72	f	none	simulated	system_sim
7915	2026-07-29	WH-BLR-01	ITM-HDD-01	0	2	44	f	none	simulated	system_sim
7916	2026-07-29	WH-BLR-01	ITM-CHG-01	0	4	208	f	none	simulated	system_sim
7917	2026-07-29	WH-BLR-01	ITM-CBL-01	0	2	221	f	none	simulated	system_sim
7918	2026-07-29	WH-CHN-01	ITM-CPU-01	0	0	59	f	none	simulated	system_sim
7919	2026-07-29	WH-CHN-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7920	2026-07-29	WH-CHN-01	ITM-RAM-01	0	9	64	f	none	simulated	system_sim
7921	2026-07-29	WH-CHN-01	ITM-SSD-01	0	1	67	f	none	simulated	system_sim
7922	2026-07-29	WH-CHN-01	ITM-HDD-01	0	1	30	f	none	simulated	system_sim
7923	2026-07-29	WH-CHN-01	ITM-CHG-01	0	10	182	f	none	simulated	system_sim
7924	2026-07-29	WH-CHN-01	ITM-CBL-01	0	10	197	f	none	simulated	system_sim
7925	2026-07-29	WH-BOM-01	ITM-CPU-01	0	3	24	f	none	simulated	system_sim
7926	2026-07-29	WH-BOM-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7927	2026-07-29	WH-BOM-01	ITM-RAM-01	0	4	55	f	none	simulated	system_sim
7928	2026-07-29	WH-BOM-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
7929	2026-07-29	WH-BOM-01	ITM-HDD-01	0	0	46	f	none	simulated	system_sim
7930	2026-07-29	WH-BOM-01	ITM-CHG-01	0	5	199	f	none	simulated	system_sim
7931	2026-07-29	WH-BOM-01	ITM-CBL-01	0	5	224	f	none	simulated	system_sim
7932	2026-07-29	WH-DEL-01	ITM-CPU-01	0	1	64	f	none	simulated	system_sim
7933	2026-07-29	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
7934	2026-07-29	WH-DEL-01	ITM-RAM-01	0	4	51	f	none	simulated	system_sim
7935	2026-07-29	WH-DEL-01	ITM-SSD-01	0	2	67	f	none	simulated	system_sim
7936	2026-07-29	WH-DEL-01	ITM-HDD-01	0	1	38	f	none	simulated	system_sim
7937	2026-07-29	WH-DEL-01	ITM-CHG-01	0	2	77	f	none	simulated	system_sim
7938	2026-07-29	WH-DEL-01	ITM-CBL-01	0	4	189	f	none	simulated	system_sim
7939	2026-07-29	WH-CCU-01	ITM-CPU-01	0	3	27	f	none	simulated	system_sim
7940	2026-07-29	WH-CCU-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7941	2026-07-29	WH-CCU-01	ITM-RAM-01	0	6	62	f	none	simulated	system_sim
7942	2026-07-29	WH-CCU-01	ITM-SSD-01	0	0	68	f	none	simulated	system_sim
7943	2026-07-29	WH-CCU-01	ITM-HDD-01	0	1	41	f	none	simulated	system_sim
7944	2026-07-29	WH-CCU-01	ITM-CHG-01	0	3	206	f	none	simulated	system_sim
7945	2026-07-29	WH-CCU-01	ITM-CBL-01	0	5	199	f	none	simulated	system_sim
7946	2026-07-30	WH-BLR-01	ITM-CPU-01	0	0	60	f	none	simulated	system_sim
7947	2026-07-30	WH-BLR-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7948	2026-07-30	WH-BLR-01	ITM-RAM-01	0	7	55	f	none	simulated	system_sim
7949	2026-07-30	WH-BLR-01	ITM-SSD-01	0	2	70	f	none	simulated	system_sim
7950	2026-07-30	WH-BLR-01	ITM-HDD-01	0	0	44	f	none	simulated	system_sim
7951	2026-07-30	WH-BLR-01	ITM-CHG-01	0	10	198	f	none	simulated	system_sim
7952	2026-07-30	WH-BLR-01	ITM-CBL-01	0	7	214	f	none	simulated	system_sim
7953	2026-07-30	WH-CHN-01	ITM-CPU-01	0	3	56	f	none	simulated	system_sim
7954	2026-07-30	WH-CHN-01	ITM-GPU-01	0	0	19	f	none	simulated	system_sim
7955	2026-07-30	WH-CHN-01	ITM-RAM-01	0	8	56	f	none	simulated	system_sim
7956	2026-07-30	WH-CHN-01	ITM-SSD-01	0	2	65	f	none	simulated	system_sim
7957	2026-07-30	WH-CHN-01	ITM-HDD-01	0	0	30	f	none	simulated	system_sim
7958	2026-07-30	WH-CHN-01	ITM-CHG-01	0	9	173	f	none	simulated	system_sim
7959	2026-07-30	WH-CHN-01	ITM-CBL-01	0	2	195	f	none	simulated	system_sim
7960	2026-07-30	WH-BOM-01	ITM-CPU-01	0	0	24	f	none	simulated	system_sim
7961	2026-07-30	WH-BOM-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7962	2026-07-30	WH-BOM-01	ITM-RAM-01	0	8	47	f	none	simulated	system_sim
7963	2026-07-30	WH-BOM-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
7964	2026-07-30	WH-BOM-01	ITM-HDD-01	0	1	45	f	none	simulated	system_sim
7965	2026-07-30	WH-BOM-01	ITM-CHG-01	0	10	189	f	none	simulated	system_sim
7966	2026-07-30	WH-BOM-01	ITM-CBL-01	0	10	214	f	none	simulated	system_sim
7967	2026-07-30	WH-DEL-01	ITM-CPU-01	0	0	64	f	none	simulated	system_sim
7968	2026-07-30	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
7969	2026-07-30	WH-DEL-01	ITM-RAM-01	0	1	50	f	none	simulated	system_sim
7970	2026-07-30	WH-DEL-01	ITM-SSD-01	0	0	67	f	none	simulated	system_sim
7971	2026-07-30	WH-DEL-01	ITM-HDD-01	0	3	35	f	none	simulated	system_sim
7972	2026-07-30	WH-DEL-01	ITM-CHG-01	0	4	73	f	none	simulated	system_sim
7973	2026-07-30	WH-DEL-01	ITM-CBL-01	0	5	184	f	none	simulated	system_sim
7974	2026-07-30	WH-CCU-01	ITM-CPU-01	0	2	25	f	none	simulated	system_sim
7975	2026-07-30	WH-CCU-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7976	2026-07-30	WH-CCU-01	ITM-RAM-01	0	4	58	f	none	simulated	system_sim
7977	2026-07-30	WH-CCU-01	ITM-SSD-01	0	0	68	f	none	simulated	system_sim
7978	2026-07-30	WH-CCU-01	ITM-HDD-01	0	0	41	f	none	simulated	system_sim
7979	2026-07-30	WH-CCU-01	ITM-CHG-01	0	5	201	f	none	simulated	system_sim
7980	2026-07-30	WH-CCU-01	ITM-CBL-01	0	6	193	f	none	simulated	system_sim
7981	2026-07-31	WH-BLR-01	ITM-CPU-01	0	3	57	f	none	simulated	system_sim
7982	2026-07-31	WH-BLR-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
7983	2026-07-31	WH-BLR-01	ITM-RAM-01	0	9	46	f	none	simulated	system_sim
7984	2026-07-31	WH-BLR-01	ITM-SSD-01	0	1	69	f	none	simulated	system_sim
7985	2026-07-31	WH-BLR-01	ITM-HDD-01	0	0	44	f	none	simulated	system_sim
7986	2026-07-31	WH-BLR-01	ITM-CHG-01	0	5	193	f	none	simulated	system_sim
7987	2026-07-31	WH-BLR-01	ITM-CBL-01	0	10	204	f	none	simulated	system_sim
7988	2026-07-31	WH-CHN-01	ITM-CPU-01	0	1	55	f	none	simulated	system_sim
7989	2026-07-31	WH-CHN-01	ITM-GPU-01	0	1	18	f	none	simulated	system_sim
7990	2026-07-31	WH-CHN-01	ITM-RAM-01	0	1	55	f	none	simulated	system_sim
7991	2026-07-31	WH-CHN-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
7992	2026-07-31	WH-CHN-01	ITM-HDD-01	0	2	28	f	none	simulated	system_sim
7993	2026-07-31	WH-CHN-01	ITM-CHG-01	0	1	172	f	none	simulated	system_sim
7994	2026-07-31	WH-CHN-01	ITM-CBL-01	0	9	186	f	none	simulated	system_sim
7995	2026-07-31	WH-BOM-01	ITM-CPU-01	0	0	24	f	none	simulated	system_sim
7996	2026-07-31	WH-BOM-01	ITM-GPU-01	0	2	15	f	none	simulated	system_sim
7997	2026-07-31	WH-BOM-01	ITM-RAM-01	0	2	45	f	none	simulated	system_sim
7998	2026-07-31	WH-BOM-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
7999	2026-07-31	WH-BOM-01	ITM-HDD-01	0	0	45	f	none	simulated	system_sim
8000	2026-07-31	WH-BOM-01	ITM-CHG-01	0	6	183	f	none	simulated	system_sim
8001	2026-07-31	WH-BOM-01	ITM-CBL-01	0	9	205	f	none	simulated	system_sim
8002	2026-07-31	WH-DEL-01	ITM-CPU-01	0	0	64	f	none	simulated	system_sim
8003	2026-07-31	WH-DEL-01	ITM-GPU-01	0	0	18	f	none	simulated	system_sim
8004	2026-07-31	WH-DEL-01	ITM-RAM-01	0	10	40	f	none	simulated	system_sim
8005	2026-07-31	WH-DEL-01	ITM-SSD-01	0	2	65	f	none	simulated	system_sim
8006	2026-07-31	WH-DEL-01	ITM-HDD-01	0	2	33	f	none	simulated	system_sim
8007	2026-07-31	WH-DEL-01	ITM-CHG-01	150	6	217	f	none	simulated	system_sim
8008	2026-07-31	WH-DEL-01	ITM-CBL-01	0	7	177	f	none	simulated	system_sim
8009	2026-07-31	WH-CCU-01	ITM-CPU-01	0	3	22	f	none	simulated	system_sim
8010	2026-07-31	WH-CCU-01	ITM-GPU-01	0	2	15	f	none	simulated	system_sim
8011	2026-07-31	WH-CCU-01	ITM-RAM-01	0	10	48	f	none	simulated	system_sim
8012	2026-07-31	WH-CCU-01	ITM-SSD-01	0	2	66	f	none	simulated	system_sim
8013	2026-07-31	WH-CCU-01	ITM-HDD-01	0	3	38	f	none	simulated	system_sim
8014	2026-07-31	WH-CCU-01	ITM-CHG-01	0	4	197	f	none	simulated	system_sim
8015	2026-07-31	WH-CCU-01	ITM-CBL-01	0	9	184	f	none	simulated	system_sim
8016	2026-08-01	WH-BLR-01	ITM-CPU-01	0	2	55	f	none	simulated	system_sim
8017	2026-08-01	WH-BLR-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
8018	2026-08-01	WH-BLR-01	ITM-RAM-01	0	9	37	f	none	simulated	system_sim
8019	2026-08-01	WH-BLR-01	ITM-SSD-01	0	3	66	f	none	simulated	system_sim
8020	2026-08-01	WH-BLR-01	ITM-HDD-01	0	3	41	f	none	simulated	system_sim
8021	2026-08-01	WH-BLR-01	ITM-CHG-01	0	6	187	f	none	simulated	system_sim
8022	2026-08-01	WH-BLR-01	ITM-CBL-01	0	2	202	f	none	simulated	system_sim
8023	2026-08-01	WH-CHN-01	ITM-CPU-01	0	3	52	f	none	simulated	system_sim
8024	2026-08-01	WH-CHN-01	ITM-GPU-01	0	1	17	f	none	simulated	system_sim
8025	2026-08-01	WH-CHN-01	ITM-RAM-01	0	10	45	f	none	simulated	system_sim
8026	2026-08-01	WH-CHN-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
8027	2026-08-01	WH-CHN-01	ITM-HDD-01	60	1	87	f	none	simulated	system_sim
8028	2026-08-01	WH-CHN-01	ITM-CHG-01	0	10	162	f	none	simulated	system_sim
8029	2026-08-01	WH-CHN-01	ITM-CBL-01	0	5	181	f	none	simulated	system_sim
8030	2026-08-01	WH-BOM-01	ITM-CPU-01	0	1	23	f	none	simulated	system_sim
8031	2026-08-01	WH-BOM-01	ITM-GPU-01	0	1	14	f	none	simulated	system_sim
8032	2026-08-01	WH-BOM-01	ITM-RAM-01	0	6	39	f	none	simulated	system_sim
8033	2026-08-01	WH-BOM-01	ITM-SSD-01	0	1	64	f	none	simulated	system_sim
8034	2026-08-01	WH-BOM-01	ITM-HDD-01	0	3	42	f	none	simulated	system_sim
8035	2026-08-01	WH-BOM-01	ITM-CHG-01	0	5	178	f	none	simulated	system_sim
8036	2026-08-01	WH-BOM-01	ITM-CBL-01	0	9	196	f	none	simulated	system_sim
8037	2026-08-01	WH-DEL-01	ITM-CPU-01	0	0	64	f	none	simulated	system_sim
8038	2026-08-01	WH-DEL-01	ITM-GPU-01	0	1	17	f	none	simulated	system_sim
8039	2026-08-01	WH-DEL-01	ITM-RAM-01	0	9	31	f	none	simulated	system_sim
8040	2026-08-01	WH-DEL-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
8041	2026-08-01	WH-DEL-01	ITM-HDD-01	0	3	30	f	none	simulated	system_sim
8042	2026-08-01	WH-DEL-01	ITM-CHG-01	0	8	209	f	none	simulated	system_sim
8043	2026-08-01	WH-DEL-01	ITM-CBL-01	0	4	173	f	none	simulated	system_sim
8044	2026-08-01	WH-CCU-01	ITM-CPU-01	45	0	67	f	none	simulated	system_sim
8045	2026-08-01	WH-CCU-01	ITM-GPU-01	0	2	13	f	none	simulated	system_sim
8046	2026-08-01	WH-CCU-01	ITM-RAM-01	0	5	43	f	none	simulated	system_sim
8047	2026-08-01	WH-CCU-01	ITM-SSD-01	0	2	64	f	none	simulated	system_sim
8048	2026-08-01	WH-CCU-01	ITM-HDD-01	0	3	35	f	none	simulated	system_sim
8049	2026-08-01	WH-CCU-01	ITM-CHG-01	0	3	194	f	none	simulated	system_sim
8050	2026-08-01	WH-CCU-01	ITM-CBL-01	0	7	177	f	none	simulated	system_sim
8051	2026-08-02	WH-BLR-01	ITM-CPU-01	0	0	55	f	none	simulated	system_sim
8052	2026-08-02	WH-BLR-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
8053	2026-08-02	WH-BLR-01	ITM-RAM-01	75	6	106	f	none	simulated	system_sim
8054	2026-08-02	WH-BLR-01	ITM-SSD-01	0	0	66	f	none	simulated	system_sim
8055	2026-08-02	WH-BLR-01	ITM-HDD-01	0	2	39	f	none	simulated	system_sim
8056	2026-08-02	WH-BLR-01	ITM-CHG-01	0	10	177	f	none	simulated	system_sim
8057	2026-08-02	WH-BLR-01	ITM-CBL-01	0	8	194	f	none	simulated	system_sim
8058	2026-08-02	WH-CHN-01	ITM-CPU-01	0	0	52	f	none	simulated	system_sim
8059	2026-08-02	WH-CHN-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
8060	2026-08-02	WH-CHN-01	ITM-RAM-01	0	3	42	f	none	simulated	system_sim
8061	2026-08-02	WH-CHN-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
8062	2026-08-02	WH-CHN-01	ITM-HDD-01	0	0	87	f	none	simulated	system_sim
8063	2026-08-02	WH-CHN-01	ITM-CHG-01	0	10	152	f	none	simulated	system_sim
8064	2026-08-02	WH-CHN-01	ITM-CBL-01	0	7	174	f	none	simulated	system_sim
8065	2026-08-02	WH-BOM-01	ITM-CPU-01	0	0	23	f	none	simulated	system_sim
8066	2026-08-02	WH-BOM-01	ITM-GPU-01	30	2	42	f	none	simulated	system_sim
8067	2026-08-02	WH-BOM-01	ITM-RAM-01	0	10	29	f	none	simulated	system_sim
8068	2026-08-02	WH-BOM-01	ITM-SSD-01	0	2	62	f	none	simulated	system_sim
8069	2026-08-02	WH-BOM-01	ITM-HDD-01	0	0	42	f	none	simulated	system_sim
8070	2026-08-02	WH-BOM-01	ITM-CHG-01	0	4	174	f	none	simulated	system_sim
8071	2026-08-02	WH-BOM-01	ITM-CBL-01	0	8	188	f	none	simulated	system_sim
8072	2026-08-02	WH-DEL-01	ITM-CPU-01	0	2	62	f	none	simulated	system_sim
8073	2026-08-02	WH-DEL-01	ITM-GPU-01	0	1	16	f	none	simulated	system_sim
8074	2026-08-02	WH-DEL-01	ITM-RAM-01	75	2	104	f	none	simulated	system_sim
8075	2026-08-02	WH-DEL-01	ITM-SSD-01	0	1	64	f	none	simulated	system_sim
8076	2026-08-02	WH-DEL-01	ITM-HDD-01	0	3	27	f	none	simulated	system_sim
8077	2026-08-02	WH-DEL-01	ITM-CHG-01	0	5	204	f	none	simulated	system_sim
8078	2026-08-02	WH-DEL-01	ITM-CBL-01	0	10	163	f	none	simulated	system_sim
8079	2026-08-02	WH-CCU-01	ITM-CPU-01	0	3	64	f	none	simulated	system_sim
8080	2026-08-02	WH-CCU-01	ITM-GPU-01	30	0	43	f	none	simulated	system_sim
8081	2026-08-02	WH-CCU-01	ITM-RAM-01	0	4	39	f	none	simulated	system_sim
8082	2026-08-02	WH-CCU-01	ITM-SSD-01	0	2	62	f	none	simulated	system_sim
8083	2026-08-02	WH-CCU-01	ITM-HDD-01	0	1	34	f	none	simulated	system_sim
8084	2026-08-02	WH-CCU-01	ITM-CHG-01	0	4	190	f	none	simulated	system_sim
8085	2026-08-02	WH-CCU-01	ITM-CBL-01	0	7	170	f	none	simulated	system_sim
8086	2026-08-03	WH-BLR-01	ITM-CPU-01	0	1	54	f	none	simulated	system_sim
8087	2026-08-03	WH-BLR-01	ITM-GPU-01	0	2	15	f	none	simulated	system_sim
8088	2026-08-03	WH-BLR-01	ITM-RAM-01	0	6	100	f	none	simulated	system_sim
8089	2026-08-03	WH-BLR-01	ITM-SSD-01	0	3	63	f	none	simulated	system_sim
8090	2026-08-03	WH-BLR-01	ITM-HDD-01	0	0	39	f	none	simulated	system_sim
8091	2026-08-03	WH-BLR-01	ITM-CHG-01	0	4	173	f	none	simulated	system_sim
8092	2026-08-03	WH-BLR-01	ITM-CBL-01	0	10	184	f	none	simulated	system_sim
8093	2026-08-03	WH-CHN-01	ITM-CPU-01	0	0	52	f	none	simulated	system_sim
8094	2026-08-03	WH-CHN-01	ITM-GPU-01	0	0	17	f	none	simulated	system_sim
8095	2026-08-03	WH-CHN-01	ITM-RAM-01	0	9	33	f	none	simulated	system_sim
8096	2026-08-03	WH-CHN-01	ITM-SSD-01	0	0	65	f	none	simulated	system_sim
8097	2026-08-03	WH-CHN-01	ITM-HDD-01	0	0	87	f	none	simulated	system_sim
8098	2026-08-03	WH-CHN-01	ITM-CHG-01	0	7	145	f	none	simulated	system_sim
8099	2026-08-03	WH-CHN-01	ITM-CBL-01	0	5	169	f	none	simulated	system_sim
8100	2026-08-03	WH-BOM-01	ITM-CPU-01	0	1	22	f	none	simulated	system_sim
8101	2026-08-03	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
8102	2026-08-03	WH-BOM-01	ITM-RAM-01	75	1	103	f	none	simulated	system_sim
8103	2026-08-03	WH-BOM-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8104	2026-08-03	WH-BOM-01	ITM-HDD-01	0	3	39	f	none	simulated	system_sim
8105	2026-08-03	WH-BOM-01	ITM-CHG-01	0	1	173	f	none	simulated	system_sim
8106	2026-08-03	WH-BOM-01	ITM-CBL-01	0	8	180	f	none	simulated	system_sim
8107	2026-08-03	WH-DEL-01	ITM-CPU-01	0	1	61	f	none	simulated	system_sim
8108	2026-08-03	WH-DEL-01	ITM-GPU-01	0	1	15	f	none	simulated	system_sim
8109	2026-08-03	WH-DEL-01	ITM-RAM-01	0	10	94	f	none	simulated	system_sim
8110	2026-08-03	WH-DEL-01	ITM-SSD-01	0	1	63	f	none	simulated	system_sim
8111	2026-08-03	WH-DEL-01	ITM-HDD-01	60	0	87	f	none	simulated	system_sim
8112	2026-08-03	WH-DEL-01	ITM-CHG-01	0	9	195	f	none	simulated	system_sim
8113	2026-08-03	WH-DEL-01	ITM-CBL-01	0	7	156	f	none	simulated	system_sim
8114	2026-08-03	WH-CCU-01	ITM-CPU-01	0	3	61	f	none	simulated	system_sim
8115	2026-08-03	WH-CCU-01	ITM-GPU-01	0	0	43	f	none	simulated	system_sim
8116	2026-08-03	WH-CCU-01	ITM-RAM-01	0	10	29	f	none	simulated	system_sim
8117	2026-08-03	WH-CCU-01	ITM-SSD-01	0	3	59	f	none	simulated	system_sim
8118	2026-08-03	WH-CCU-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
8119	2026-08-03	WH-CCU-01	ITM-CHG-01	0	9	181	f	none	simulated	system_sim
8120	2026-08-03	WH-CCU-01	ITM-CBL-01	0	5	165	f	none	simulated	system_sim
8121	2026-08-04	WH-BLR-01	ITM-CPU-01	0	3	51	f	none	simulated	system_sim
8122	2026-08-04	WH-BLR-01	ITM-GPU-01	0	1	14	f	none	simulated	system_sim
8123	2026-08-04	WH-BLR-01	ITM-RAM-01	0	8	92	f	none	simulated	system_sim
8124	2026-08-04	WH-BLR-01	ITM-SSD-01	0	0	63	f	none	simulated	system_sim
8125	2026-08-04	WH-BLR-01	ITM-HDD-01	0	2	37	f	none	simulated	system_sim
8126	2026-08-04	WH-BLR-01	ITM-CHG-01	0	4	169	f	none	simulated	system_sim
8127	2026-08-04	WH-BLR-01	ITM-CBL-01	0	8	176	f	none	simulated	system_sim
8128	2026-08-04	WH-CHN-01	ITM-CPU-01	0	0	52	f	none	simulated	system_sim
8129	2026-08-04	WH-CHN-01	ITM-GPU-01	0	2	15	f	none	simulated	system_sim
8130	2026-08-04	WH-CHN-01	ITM-RAM-01	75	10	98	f	none	simulated	system_sim
8131	2026-08-04	WH-CHN-01	ITM-SSD-01	0	1	64	f	none	simulated	system_sim
8132	2026-08-04	WH-CHN-01	ITM-HDD-01	0	1	86	f	none	simulated	system_sim
8133	2026-08-04	WH-CHN-01	ITM-CHG-01	0	10	135	f	none	simulated	system_sim
8134	2026-08-04	WH-CHN-01	ITM-CBL-01	0	9	160	f	none	simulated	system_sim
8135	2026-08-04	WH-BOM-01	ITM-CPU-01	45	0	67	f	none	simulated	system_sim
8136	2026-08-04	WH-BOM-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
8137	2026-08-04	WH-BOM-01	ITM-RAM-01	0	5	98	f	none	simulated	system_sim
8138	2026-08-04	WH-BOM-01	ITM-SSD-01	0	3	59	f	none	simulated	system_sim
8139	2026-08-04	WH-BOM-01	ITM-HDD-01	0	2	37	f	none	simulated	system_sim
8140	2026-08-04	WH-BOM-01	ITM-CHG-01	0	8	165	f	none	simulated	system_sim
8141	2026-08-04	WH-BOM-01	ITM-CBL-01	0	3	177	f	none	simulated	system_sim
8142	2026-08-04	WH-DEL-01	ITM-CPU-01	0	1	60	f	none	simulated	system_sim
8143	2026-08-04	WH-DEL-01	ITM-GPU-01	0	2	13	f	none	simulated	system_sim
8144	2026-08-04	WH-DEL-01	ITM-RAM-01	0	2	92	f	none	simulated	system_sim
8145	2026-08-04	WH-DEL-01	ITM-SSD-01	0	0	63	f	none	simulated	system_sim
8146	2026-08-04	WH-DEL-01	ITM-HDD-01	0	0	87	f	none	simulated	system_sim
8147	2026-08-04	WH-DEL-01	ITM-CHG-01	0	10	185	f	none	simulated	system_sim
8148	2026-08-04	WH-DEL-01	ITM-CBL-01	0	10	146	f	none	simulated	system_sim
8149	2026-08-04	WH-CCU-01	ITM-CPU-01	0	3	58	f	none	simulated	system_sim
8150	2026-08-04	WH-CCU-01	ITM-GPU-01	0	1	42	f	none	simulated	system_sim
8151	2026-08-04	WH-CCU-01	ITM-RAM-01	75	1	103	f	none	simulated	system_sim
8152	2026-08-04	WH-CCU-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
8153	2026-08-04	WH-CCU-01	ITM-HDD-01	0	3	31	f	none	simulated	system_sim
8154	2026-08-04	WH-CCU-01	ITM-CHG-01	0	6	175	f	none	simulated	system_sim
8155	2026-08-04	WH-CCU-01	ITM-CBL-01	0	5	160	f	none	simulated	system_sim
8156	2026-08-05	WH-BLR-01	ITM-CPU-01	0	2	49	f	none	simulated	system_sim
8157	2026-08-05	WH-BLR-01	ITM-GPU-01	30	0	34	t	shrinkage	simulated	system_sim
8158	2026-08-05	WH-BLR-01	ITM-RAM-01	0	3	89	f	none	simulated	system_sim
8159	2026-08-05	WH-BLR-01	ITM-SSD-01	0	0	63	f	none	simulated	system_sim
8160	2026-08-05	WH-BLR-01	ITM-HDD-01	0	1	36	f	none	simulated	system_sim
8161	2026-08-05	WH-BLR-01	ITM-CHG-01	0	1	168	f	none	simulated	system_sim
8162	2026-08-05	WH-BLR-01	ITM-CBL-01	0	9	167	f	none	simulated	system_sim
8163	2026-08-05	WH-CHN-01	ITM-CPU-01	0	3	49	f	none	simulated	system_sim
8164	2026-08-05	WH-CHN-01	ITM-GPU-01	0	1	14	f	none	simulated	system_sim
8165	2026-08-05	WH-CHN-01	ITM-RAM-01	0	8	90	f	none	simulated	system_sim
8166	2026-08-05	WH-CHN-01	ITM-SSD-01	0	2	62	f	none	simulated	system_sim
8167	2026-08-05	WH-CHN-01	ITM-HDD-01	0	0	86	f	none	simulated	system_sim
8168	2026-08-05	WH-CHN-01	ITM-CHG-01	0	5	130	f	none	simulated	system_sim
8169	2026-08-05	WH-CHN-01	ITM-CBL-01	0	4	156	f	none	simulated	system_sim
8170	2026-08-05	WH-BOM-01	ITM-CPU-01	0	0	67	f	none	simulated	system_sim
8171	2026-08-05	WH-BOM-01	ITM-GPU-01	0	1	41	f	none	simulated	system_sim
8172	2026-08-05	WH-BOM-01	ITM-RAM-01	0	6	92	f	none	simulated	system_sim
8173	2026-08-05	WH-BOM-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
8174	2026-08-05	WH-BOM-01	ITM-HDD-01	0	3	34	f	none	simulated	system_sim
8175	2026-08-05	WH-BOM-01	ITM-CHG-01	0	8	157	f	none	simulated	system_sim
8176	2026-08-05	WH-BOM-01	ITM-CBL-01	0	6	171	f	none	simulated	system_sim
8177	2026-08-05	WH-DEL-01	ITM-CPU-01	0	2	58	f	none	simulated	system_sim
8178	2026-08-05	WH-DEL-01	ITM-GPU-01	30	1	42	f	none	simulated	system_sim
8179	2026-08-05	WH-DEL-01	ITM-RAM-01	0	9	83	f	none	simulated	system_sim
8180	2026-08-05	WH-DEL-01	ITM-SSD-01	0	1	62	f	none	simulated	system_sim
8181	2026-08-05	WH-DEL-01	ITM-HDD-01	0	0	87	f	none	simulated	system_sim
8182	2026-08-05	WH-DEL-01	ITM-CHG-01	0	10	175	f	none	simulated	system_sim
8183	2026-08-05	WH-DEL-01	ITM-CBL-01	300	8	438	f	none	simulated	system_sim
8184	2026-08-05	WH-CCU-01	ITM-CPU-01	0	3	55	f	none	simulated	system_sim
8185	2026-08-05	WH-CCU-01	ITM-GPU-01	0	0	42	f	none	simulated	system_sim
8186	2026-08-05	WH-CCU-01	ITM-RAM-01	0	4	99	f	none	simulated	system_sim
8187	2026-08-05	WH-CCU-01	ITM-SSD-01	0	3	56	f	none	simulated	system_sim
8188	2026-08-05	WH-CCU-01	ITM-HDD-01	0	0	31	f	none	simulated	system_sim
8189	2026-08-05	WH-CCU-01	ITM-CHG-01	0	8	167	f	none	simulated	system_sim
8190	2026-08-05	WH-CCU-01	ITM-CBL-01	0	9	151	f	none	simulated	system_sim
8191	2026-08-06	WH-BLR-01	ITM-CPU-01	0	1	48	f	none	simulated	system_sim
8192	2026-08-06	WH-BLR-01	ITM-GPU-01	0	1	33	f	none	simulated	system_sim
8193	2026-08-06	WH-BLR-01	ITM-RAM-01	0	6	83	f	none	simulated	system_sim
8194	2026-08-06	WH-BLR-01	ITM-SSD-01	0	1	62	f	none	simulated	system_sim
8195	2026-08-06	WH-BLR-01	ITM-HDD-01	0	2	34	f	none	simulated	system_sim
8196	2026-08-06	WH-BLR-01	ITM-CHG-01	0	9	159	f	none	simulated	system_sim
8197	2026-08-06	WH-BLR-01	ITM-CBL-01	0	6	161	f	none	simulated	system_sim
8198	2026-08-06	WH-CHN-01	ITM-CPU-01	0	3	46	f	none	simulated	system_sim
8199	2026-08-06	WH-CHN-01	ITM-GPU-01	30	0	44	f	none	simulated	system_sim
8200	2026-08-06	WH-CHN-01	ITM-RAM-01	0	9	81	f	none	simulated	system_sim
8201	2026-08-06	WH-CHN-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8202	2026-08-06	WH-CHN-01	ITM-HDD-01	0	0	86	f	none	simulated	system_sim
8203	2026-08-06	WH-CHN-01	ITM-CHG-01	0	6	124	f	none	simulated	system_sim
8204	2026-08-06	WH-CHN-01	ITM-CBL-01	0	10	146	f	none	simulated	system_sim
8205	2026-08-06	WH-BOM-01	ITM-CPU-01	0	1	66	f	none	simulated	system_sim
8206	2026-08-06	WH-BOM-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8207	2026-08-06	WH-BOM-01	ITM-RAM-01	0	5	87	f	none	simulated	system_sim
8208	2026-08-06	WH-BOM-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
8209	2026-08-06	WH-BOM-01	ITM-HDD-01	0	0	34	f	none	simulated	system_sim
8210	2026-08-06	WH-BOM-01	ITM-CHG-01	0	7	150	f	none	simulated	system_sim
8211	2026-08-06	WH-BOM-01	ITM-CBL-01	0	3	168	f	none	simulated	system_sim
8212	2026-08-06	WH-DEL-01	ITM-CPU-01	0	2	56	f	none	simulated	system_sim
8213	2026-08-06	WH-DEL-01	ITM-GPU-01	0	1	41	f	none	simulated	system_sim
8214	2026-08-06	WH-DEL-01	ITM-RAM-01	0	8	75	f	none	simulated	system_sim
8215	2026-08-06	WH-DEL-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8216	2026-08-06	WH-DEL-01	ITM-HDD-01	0	1	86	f	none	simulated	system_sim
8217	2026-08-06	WH-DEL-01	ITM-CHG-01	0	4	171	f	none	simulated	system_sim
8218	2026-08-06	WH-DEL-01	ITM-CBL-01	0	9	429	f	none	simulated	system_sim
8219	2026-08-06	WH-CCU-01	ITM-CPU-01	0	2	53	f	none	simulated	system_sim
8220	2026-08-06	WH-CCU-01	ITM-GPU-01	0	2	40	f	none	simulated	system_sim
8221	2026-08-06	WH-CCU-01	ITM-RAM-01	0	2	97	f	none	simulated	system_sim
8222	2026-08-06	WH-CCU-01	ITM-SSD-01	0	0	56	f	none	simulated	system_sim
8223	2026-08-06	WH-CCU-01	ITM-HDD-01	0	3	28	f	none	simulated	system_sim
8224	2026-08-06	WH-CCU-01	ITM-CHG-01	0	10	157	f	none	simulated	system_sim
8225	2026-08-06	WH-CCU-01	ITM-CBL-01	0	1	150	f	none	simulated	system_sim
8226	2026-08-07	WH-BLR-01	ITM-CPU-01	0	2	46	f	none	simulated	system_sim
8227	2026-08-07	WH-BLR-01	ITM-GPU-01	0	0	33	f	none	simulated	system_sim
8228	2026-08-07	WH-BLR-01	ITM-RAM-01	0	9	74	f	none	simulated	system_sim
8229	2026-08-07	WH-BLR-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8230	2026-08-07	WH-BLR-01	ITM-HDD-01	0	2	32	f	none	simulated	system_sim
8231	2026-08-07	WH-BLR-01	ITM-CHG-01	0	8	151	f	none	simulated	system_sim
8232	2026-08-07	WH-BLR-01	ITM-CBL-01	0	9	152	f	none	simulated	system_sim
8233	2026-08-07	WH-CHN-01	ITM-CPU-01	0	0	46	f	none	simulated	system_sim
8234	2026-08-07	WH-CHN-01	ITM-GPU-01	0	0	44	f	none	simulated	system_sim
8235	2026-08-07	WH-CHN-01	ITM-RAM-01	0	2	79	f	none	simulated	system_sim
8236	2026-08-07	WH-CHN-01	ITM-SSD-01	0	3	59	f	none	simulated	system_sim
8237	2026-08-07	WH-CHN-01	ITM-HDD-01	0	0	86	f	none	simulated	system_sim
8238	2026-08-07	WH-CHN-01	ITM-CHG-01	0	1	123	f	none	simulated	system_sim
8239	2026-08-07	WH-CHN-01	ITM-CBL-01	300	6	440	f	none	simulated	system_sim
8240	2026-08-07	WH-BOM-01	ITM-CPU-01	0	1	65	f	none	simulated	system_sim
8241	2026-08-07	WH-BOM-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8242	2026-08-07	WH-BOM-01	ITM-RAM-01	0	10	77	f	none	simulated	system_sim
8243	2026-08-07	WH-BOM-01	ITM-SSD-01	0	1	58	f	none	simulated	system_sim
8244	2026-08-07	WH-BOM-01	ITM-HDD-01	0	2	32	f	none	simulated	system_sim
8245	2026-08-07	WH-BOM-01	ITM-CHG-01	0	8	142	f	none	simulated	system_sim
8246	2026-08-07	WH-BOM-01	ITM-CBL-01	0	7	161	f	none	simulated	system_sim
8247	2026-08-07	WH-DEL-01	ITM-CPU-01	0	2	54	f	none	simulated	system_sim
8248	2026-08-07	WH-DEL-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8249	2026-08-07	WH-DEL-01	ITM-RAM-01	0	6	69	f	none	simulated	system_sim
8250	2026-08-07	WH-DEL-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8251	2026-08-07	WH-DEL-01	ITM-HDD-01	0	3	83	f	none	simulated	system_sim
8252	2026-08-07	WH-DEL-01	ITM-CHG-01	0	2	169	f	none	simulated	system_sim
8253	2026-08-07	WH-DEL-01	ITM-CBL-01	0	4	425	f	none	simulated	system_sim
8254	2026-08-07	WH-CCU-01	ITM-CPU-01	0	3	50	f	none	simulated	system_sim
8255	2026-08-07	WH-CCU-01	ITM-GPU-01	0	0	40	f	none	simulated	system_sim
8256	2026-08-07	WH-CCU-01	ITM-RAM-01	0	5	92	f	none	simulated	system_sim
8257	2026-08-07	WH-CCU-01	ITM-SSD-01	0	0	56	f	none	simulated	system_sim
8258	2026-08-07	WH-CCU-01	ITM-HDD-01	60	2	86	f	none	simulated	system_sim
8259	2026-08-07	WH-CCU-01	ITM-CHG-01	0	4	153	f	none	simulated	system_sim
8260	2026-08-07	WH-CCU-01	ITM-CBL-01	0	6	144	f	none	simulated	system_sim
8261	2026-08-08	WH-BLR-01	ITM-CPU-01	0	3	43	f	none	simulated	system_sim
8262	2026-08-08	WH-BLR-01	ITM-GPU-01	0	0	33	f	none	simulated	system_sim
8263	2026-08-08	WH-BLR-01	ITM-RAM-01	0	10	64	f	none	simulated	system_sim
8264	2026-08-08	WH-BLR-01	ITM-SSD-01	0	0	62	f	none	simulated	system_sim
8265	2026-08-08	WH-BLR-01	ITM-HDD-01	0	1	31	f	none	simulated	system_sim
8266	2026-08-08	WH-BLR-01	ITM-CHG-01	0	1	150	f	none	simulated	system_sim
8267	2026-08-08	WH-BLR-01	ITM-CBL-01	0	3	149	f	none	simulated	system_sim
8268	2026-08-08	WH-CHN-01	ITM-CPU-01	0	0	46	f	none	simulated	system_sim
8269	2026-08-08	WH-CHN-01	ITM-GPU-01	0	1	43	f	none	simulated	system_sim
8270	2026-08-08	WH-CHN-01	ITM-RAM-01	0	5	74	f	none	simulated	system_sim
8271	2026-08-08	WH-CHN-01	ITM-SSD-01	0	3	56	f	none	simulated	system_sim
8272	2026-08-08	WH-CHN-01	ITM-HDD-01	0	3	83	f	none	simulated	system_sim
8273	2026-08-08	WH-CHN-01	ITM-CHG-01	0	6	117	f	none	simulated	system_sim
8274	2026-08-08	WH-CHN-01	ITM-CBL-01	0	7	433	f	none	simulated	system_sim
8275	2026-08-08	WH-BOM-01	ITM-CPU-01	0	2	63	f	none	simulated	system_sim
8276	2026-08-08	WH-BOM-01	ITM-GPU-01	0	2	39	f	none	simulated	system_sim
8277	2026-08-08	WH-BOM-01	ITM-RAM-01	0	9	68	f	none	simulated	system_sim
8278	2026-08-08	WH-BOM-01	ITM-SSD-01	0	0	58	f	none	simulated	system_sim
8279	2026-08-08	WH-BOM-01	ITM-HDD-01	0	1	31	f	none	simulated	system_sim
8280	2026-08-08	WH-BOM-01	ITM-CHG-01	0	6	136	f	none	simulated	system_sim
8281	2026-08-08	WH-BOM-01	ITM-CBL-01	0	4	157	f	none	simulated	system_sim
8282	2026-08-08	WH-DEL-01	ITM-CPU-01	0	3	51	f	none	simulated	system_sim
8283	2026-08-08	WH-DEL-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8284	2026-08-08	WH-DEL-01	ITM-RAM-01	0	8	61	f	none	simulated	system_sim
8285	2026-08-08	WH-DEL-01	ITM-SSD-01	0	3	59	f	none	simulated	system_sim
8286	2026-08-08	WH-DEL-01	ITM-HDD-01	0	0	83	f	none	simulated	system_sim
8287	2026-08-08	WH-DEL-01	ITM-CHG-01	0	4	165	f	none	simulated	system_sim
8288	2026-08-08	WH-DEL-01	ITM-CBL-01	0	2	423	f	none	simulated	system_sim
8289	2026-08-08	WH-CCU-01	ITM-CPU-01	0	3	47	f	none	simulated	system_sim
8290	2026-08-08	WH-CCU-01	ITM-GPU-01	0	2	38	f	none	simulated	system_sim
8291	2026-08-08	WH-CCU-01	ITM-RAM-01	0	3	89	f	none	simulated	system_sim
8292	2026-08-08	WH-CCU-01	ITM-SSD-01	0	3	53	f	none	simulated	system_sim
8293	2026-08-08	WH-CCU-01	ITM-HDD-01	0	2	84	f	none	simulated	system_sim
8294	2026-08-08	WH-CCU-01	ITM-CHG-01	0	4	149	f	none	simulated	system_sim
8295	2026-08-08	WH-CCU-01	ITM-CBL-01	300	9	435	f	none	simulated	system_sim
8296	2026-08-09	WH-BLR-01	ITM-CPU-01	0	0	43	f	none	simulated	system_sim
8297	2026-08-09	WH-BLR-01	ITM-GPU-01	0	0	33	f	none	simulated	system_sim
8298	2026-08-09	WH-BLR-01	ITM-RAM-01	0	6	58	f	none	simulated	system_sim
8299	2026-08-09	WH-BLR-01	ITM-SSD-01	0	1	61	f	none	simulated	system_sim
8300	2026-08-09	WH-BLR-01	ITM-HDD-01	0	0	31	f	none	simulated	system_sim
8301	2026-08-09	WH-BLR-01	ITM-CHG-01	0	4	146	f	none	simulated	system_sim
8302	2026-08-09	WH-BLR-01	ITM-CBL-01	300	7	442	f	none	simulated	system_sim
8303	2026-08-09	WH-CHN-01	ITM-CPU-01	0	1	45	f	none	simulated	system_sim
8304	2026-08-09	WH-CHN-01	ITM-GPU-01	0	0	43	f	none	simulated	system_sim
8305	2026-08-09	WH-CHN-01	ITM-RAM-01	0	9	65	f	none	simulated	system_sim
8306	2026-08-09	WH-CHN-01	ITM-SSD-01	0	0	56	f	none	simulated	system_sim
8307	2026-08-09	WH-CHN-01	ITM-HDD-01	0	0	83	f	none	simulated	system_sim
8308	2026-08-09	WH-CHN-01	ITM-CHG-01	0	10	107	f	none	simulated	system_sim
8309	2026-08-09	WH-CHN-01	ITM-CBL-01	0	6	427	f	none	simulated	system_sim
8310	2026-08-09	WH-BOM-01	ITM-CPU-01	0	0	63	f	none	simulated	system_sim
8311	2026-08-09	WH-BOM-01	ITM-GPU-01	0	0	39	f	none	simulated	system_sim
8312	2026-08-09	WH-BOM-01	ITM-RAM-01	0	6	62	f	none	simulated	system_sim
8313	2026-08-09	WH-BOM-01	ITM-SSD-01	0	2	56	f	none	simulated	system_sim
8314	2026-08-09	WH-BOM-01	ITM-HDD-01	0	0	31	f	none	simulated	system_sim
8315	2026-08-09	WH-BOM-01	ITM-CHG-01	0	7	129	f	none	simulated	system_sim
8316	2026-08-09	WH-BOM-01	ITM-CBL-01	0	6	151	f	none	simulated	system_sim
8317	2026-08-09	WH-DEL-01	ITM-CPU-01	0	0	51	f	none	simulated	system_sim
8318	2026-08-09	WH-DEL-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8319	2026-08-09	WH-DEL-01	ITM-RAM-01	0	6	55	f	none	simulated	system_sim
8320	2026-08-09	WH-DEL-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
8321	2026-08-09	WH-DEL-01	ITM-HDD-01	0	0	83	f	none	simulated	system_sim
8322	2026-08-09	WH-DEL-01	ITM-CHG-01	0	2	163	f	none	simulated	system_sim
8323	2026-08-09	WH-DEL-01	ITM-CBL-01	0	1	422	f	none	simulated	system_sim
8324	2026-08-09	WH-CCU-01	ITM-CPU-01	0	3	44	f	none	simulated	system_sim
8325	2026-08-09	WH-CCU-01	ITM-GPU-01	0	2	36	f	none	simulated	system_sim
8326	2026-08-09	WH-CCU-01	ITM-RAM-01	0	8	81	f	none	simulated	system_sim
8327	2026-08-09	WH-CCU-01	ITM-SSD-01	0	3	50	f	none	simulated	system_sim
8328	2026-08-09	WH-CCU-01	ITM-HDD-01	0	3	81	f	none	simulated	system_sim
8329	2026-08-09	WH-CCU-01	ITM-CHG-01	0	10	139	f	none	simulated	system_sim
8330	2026-08-09	WH-CCU-01	ITM-CBL-01	0	1	434	f	none	simulated	system_sim
8331	2026-08-10	WH-BLR-01	ITM-CPU-01	0	3	40	f	none	simulated	system_sim
8332	2026-08-10	WH-BLR-01	ITM-GPU-01	0	0	33	f	none	simulated	system_sim
8333	2026-08-10	WH-BLR-01	ITM-RAM-01	0	5	53	f	none	simulated	system_sim
8334	2026-08-10	WH-BLR-01	ITM-SSD-01	0	1	60	f	none	simulated	system_sim
8335	2026-08-10	WH-BLR-01	ITM-HDD-01	0	2	29	f	none	simulated	system_sim
8336	2026-08-10	WH-BLR-01	ITM-CHG-01	0	4	142	f	none	simulated	system_sim
8337	2026-08-10	WH-BLR-01	ITM-CBL-01	0	9	433	f	none	simulated	system_sim
8338	2026-08-10	WH-CHN-01	ITM-CPU-01	0	2	43	f	none	simulated	system_sim
8339	2026-08-10	WH-CHN-01	ITM-GPU-01	0	0	43	f	none	simulated	system_sim
8340	2026-08-10	WH-CHN-01	ITM-RAM-01	0	8	57	f	none	simulated	system_sim
8341	2026-08-10	WH-CHN-01	ITM-SSD-01	0	2	54	f	none	simulated	system_sim
8342	2026-08-10	WH-CHN-01	ITM-HDD-01	0	0	83	f	none	simulated	system_sim
8343	2026-08-10	WH-CHN-01	ITM-CHG-01	0	9	98	f	none	simulated	system_sim
8344	2026-08-10	WH-CHN-01	ITM-CBL-01	0	6	421	f	none	simulated	system_sim
8345	2026-08-10	WH-BOM-01	ITM-CPU-01	0	0	63	f	none	simulated	system_sim
8346	2026-08-10	WH-BOM-01	ITM-GPU-01	0	1	38	f	none	simulated	system_sim
8347	2026-08-10	WH-BOM-01	ITM-RAM-01	0	8	54	f	none	simulated	system_sim
8348	2026-08-10	WH-BOM-01	ITM-SSD-01	0	1	55	f	none	simulated	system_sim
8349	2026-08-10	WH-BOM-01	ITM-HDD-01	0	2	29	f	none	simulated	system_sim
8350	2026-08-10	WH-BOM-01	ITM-CHG-01	0	10	119	f	none	simulated	system_sim
8351	2026-08-10	WH-BOM-01	ITM-CBL-01	0	7	144	f	none	simulated	system_sim
8352	2026-08-10	WH-DEL-01	ITM-CPU-01	0	2	49	f	none	simulated	system_sim
8353	2026-08-10	WH-DEL-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8354	2026-08-10	WH-DEL-01	ITM-RAM-01	0	7	48	f	none	simulated	system_sim
8355	2026-08-10	WH-DEL-01	ITM-SSD-01	0	0	59	f	none	simulated	system_sim
8356	2026-08-10	WH-DEL-01	ITM-HDD-01	0	2	81	f	none	simulated	system_sim
8357	2026-08-10	WH-DEL-01	ITM-CHG-01	0	10	153	f	none	simulated	system_sim
8358	2026-08-10	WH-DEL-01	ITM-CBL-01	0	10	412	f	none	simulated	system_sim
8359	2026-08-10	WH-CCU-01	ITM-CPU-01	0	1	43	f	none	simulated	system_sim
8360	2026-08-10	WH-CCU-01	ITM-GPU-01	0	2	34	f	none	simulated	system_sim
8361	2026-08-10	WH-CCU-01	ITM-RAM-01	0	8	73	f	none	simulated	system_sim
8362	2026-08-10	WH-CCU-01	ITM-SSD-01	0	1	49	f	none	simulated	system_sim
8363	2026-08-10	WH-CCU-01	ITM-HDD-01	0	0	81	f	none	simulated	system_sim
8364	2026-08-10	WH-CCU-01	ITM-CHG-01	0	2	137	f	none	simulated	system_sim
8365	2026-08-10	WH-CCU-01	ITM-CBL-01	0	2	432	f	none	simulated	system_sim
8366	2026-08-11	WH-BLR-01	ITM-CPU-01	0	2	38	f	none	simulated	system_sim
8367	2026-08-11	WH-BLR-01	ITM-GPU-01	0	1	32	f	none	simulated	system_sim
8368	2026-08-11	WH-BLR-01	ITM-RAM-01	0	9	44	f	none	simulated	system_sim
8369	2026-08-11	WH-BLR-01	ITM-SSD-01	0	0	60	f	none	simulated	system_sim
8370	2026-08-11	WH-BLR-01	ITM-HDD-01	60	2	87	f	none	simulated	system_sim
8371	2026-08-11	WH-BLR-01	ITM-CHG-01	0	6	136	f	none	simulated	system_sim
8372	2026-08-11	WH-BLR-01	ITM-CBL-01	0	2	431	f	none	simulated	system_sim
8373	2026-08-11	WH-CHN-01	ITM-CPU-01	0	1	42	f	none	simulated	system_sim
8374	2026-08-11	WH-CHN-01	ITM-GPU-01	0	2	41	f	none	simulated	system_sim
8375	2026-08-11	WH-CHN-01	ITM-RAM-01	0	9	48	f	none	simulated	system_sim
8376	2026-08-11	WH-CHN-01	ITM-SSD-01	0	0	54	f	none	simulated	system_sim
8377	2026-08-11	WH-CHN-01	ITM-HDD-01	0	0	83	f	none	simulated	system_sim
8378	2026-08-11	WH-CHN-01	ITM-CHG-01	0	2	96	f	none	simulated	system_sim
8379	2026-08-11	WH-CHN-01	ITM-CBL-01	0	9	412	f	none	simulated	system_sim
8380	2026-08-11	WH-BOM-01	ITM-CPU-01	0	3	60	f	none	simulated	system_sim
8381	2026-08-11	WH-BOM-01	ITM-GPU-01	0	0	38	f	none	simulated	system_sim
8382	2026-08-11	WH-BOM-01	ITM-RAM-01	0	2	52	f	none	simulated	system_sim
8383	2026-08-11	WH-BOM-01	ITM-SSD-01	0	3	52	f	none	simulated	system_sim
8384	2026-08-11	WH-BOM-01	ITM-HDD-01	60	3	86	f	none	simulated	system_sim
8385	2026-08-11	WH-BOM-01	ITM-CHG-01	0	4	115	f	none	simulated	system_sim
8386	2026-08-11	WH-BOM-01	ITM-CBL-01	300	2	442	f	none	simulated	system_sim
8387	2026-08-11	WH-DEL-01	ITM-CPU-01	0	0	49	f	none	simulated	system_sim
8388	2026-08-11	WH-DEL-01	ITM-GPU-01	0	0	41	f	none	simulated	system_sim
8389	2026-08-11	WH-DEL-01	ITM-RAM-01	0	4	44	f	none	simulated	system_sim
8390	2026-08-11	WH-DEL-01	ITM-SSD-01	0	3	56	f	none	simulated	system_sim
8391	2026-08-11	WH-DEL-01	ITM-HDD-01	0	0	81	f	none	simulated	system_sim
8392	2026-08-11	WH-DEL-01	ITM-CHG-01	0	4	149	f	none	simulated	system_sim
8393	2026-08-11	WH-DEL-01	ITM-CBL-01	0	6	406	f	none	simulated	system_sim
8394	2026-08-11	WH-CCU-01	ITM-CPU-01	0	2	41	f	none	simulated	system_sim
8395	2026-08-11	WH-CCU-01	ITM-GPU-01	0	2	32	f	none	simulated	system_sim
8396	2026-08-11	WH-CCU-01	ITM-RAM-01	0	1	72	f	none	simulated	system_sim
8397	2026-08-11	WH-CCU-01	ITM-SSD-01	0	0	49	f	none	simulated	system_sim
8398	2026-08-11	WH-CCU-01	ITM-HDD-01	0	0	81	f	none	simulated	system_sim
8399	2026-08-11	WH-CCU-01	ITM-CHG-01	0	5	132	f	none	simulated	system_sim
8400	2026-08-11	WH-CCU-01	ITM-CBL-01	0	9	423	f	none	simulated	system_sim
\.


--
-- Data for Name: system_health_snapshots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_health_snapshots (id, service, status, latency_ms, "timestamp") FROM stdin;
1	database	HEALTHY	0	2026-08-19 15:43:16.958992
2	redis	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
3	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
4	celery	NOT_CONFIGURED	\N	2026-08-19 15:43:16.958992
5	email	HEALTHY	\N	2026-08-19 15:43:16.958992
6	backup	DEGRADED	\N	2026-08-19 15:43:16.960009
7	sentry	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
8	openai	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
9	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:43:16.960009
10	simulation	HEALTHY	\N	2026-08-19 15:43:16.960009
11	application	HEALTHY	4.5	2026-08-19 15:43:16.960009
12	database	HEALTHY	5.94	2026-08-19 15:43:47.085618
13	redis	NOT_CONFIGURED	\N	2026-08-19 15:43:47.085618
14	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
15	celery	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
16	email	HEALTHY	\N	2026-08-19 15:43:47.086299
17	backup	DEGRADED	\N	2026-08-19 15:43:47.086299
18	sentry	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
19	openai	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
20	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:43:47.086299
21	simulation	HEALTHY	\N	2026-08-19 15:43:47.086299
22	application	HEALTHY	4.5	2026-08-19 15:43:47.086299
23	database	HEALTHY	3.02	2026-08-19 15:44:17.211859
24	redis	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
25	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
26	celery	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
27	email	HEALTHY	\N	2026-08-19 15:44:17.211859
28	backup	DEGRADED	\N	2026-08-19 15:44:17.211859
29	sentry	NOT_CONFIGURED	\N	2026-08-19 15:44:17.211859
30	openai	NOT_CONFIGURED	\N	2026-08-19 15:44:17.212864
31	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:44:17.212864
32	simulation	HEALTHY	\N	2026-08-19 15:44:17.212864
33	application	HEALTHY	4.5	2026-08-19 15:44:17.212864
34	database	HEALTHY	5.99	2026-08-19 15:44:47.457941
35	redis	NOT_CONFIGURED	\N	2026-08-19 15:44:47.457941
36	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
37	celery	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
38	email	HEALTHY	\N	2026-08-19 15:44:47.458945
39	backup	DEGRADED	\N	2026-08-19 15:44:47.458945
40	sentry	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
41	openai	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
42	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:44:47.458945
43	simulation	HEALTHY	\N	2026-08-19 15:44:47.458945
44	application	HEALTHY	4.5	2026-08-19 15:44:47.458945
45	database	HEALTHY	3.71	2026-08-19 15:45:17.632382
46	redis	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
47	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
48	celery	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
49	email	HEALTHY	\N	2026-08-19 15:45:17.632382
50	backup	DEGRADED	\N	2026-08-19 15:45:17.632382
51	sentry	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
52	openai	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
53	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:45:17.632382
54	simulation	HEALTHY	\N	2026-08-19 15:45:17.632382
55	application	HEALTHY	4.5	2026-08-19 15:45:17.632382
56	database	HEALTHY	1	2026-08-19 15:45:47.689904
57	redis	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
58	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
59	celery	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
60	email	HEALTHY	\N	2026-08-19 15:45:47.689904
61	backup	DEGRADED	\N	2026-08-19 15:45:47.689904
62	sentry	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
63	openai	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
64	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:45:47.689904
65	simulation	HEALTHY	\N	2026-08-19 15:45:47.689904
66	application	HEALTHY	4.5	2026-08-19 15:45:47.689904
67	database	HEALTHY	1	2026-08-19 15:46:17.753805
68	redis	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
69	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
70	celery	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
71	email	HEALTHY	\N	2026-08-19 15:46:17.753805
72	backup	DEGRADED	\N	2026-08-19 15:46:17.753805
73	sentry	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
74	openai	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
75	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:46:17.753805
76	simulation	HEALTHY	\N	2026-08-19 15:46:17.753805
77	application	HEALTHY	4.5	2026-08-19 15:46:17.753805
78	database	HEALTHY	1	2026-08-19 15:46:47.800965
79	redis	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
80	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
81	celery	NOT_CONFIGURED	\N	2026-08-19 15:46:47.800965
82	email	HEALTHY	\N	2026-08-19 15:46:47.80197
83	backup	DEGRADED	\N	2026-08-19 15:46:47.80197
84	sentry	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
85	openai	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
86	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:46:47.80197
87	simulation	HEALTHY	\N	2026-08-19 15:46:47.80197
88	application	HEALTHY	4.5	2026-08-19 15:46:47.80197
89	database	HEALTHY	0	2026-08-19 15:47:17.84018
90	redis	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
91	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
92	celery	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
93	email	HEALTHY	\N	2026-08-19 15:47:17.84018
94	backup	DEGRADED	\N	2026-08-19 15:47:17.84018
95	sentry	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
96	openai	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
97	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:47:17.84018
98	simulation	HEALTHY	\N	2026-08-19 15:47:17.84018
99	application	HEALTHY	4.5	2026-08-19 15:47:17.84018
100	database	HEALTHY	0	2026-08-19 15:47:47.878138
101	redis	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
102	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
103	celery	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
104	email	HEALTHY	\N	2026-08-19 15:47:47.878138
105	backup	DEGRADED	\N	2026-08-19 15:47:47.878138
106	sentry	NOT_CONFIGURED	\N	2026-08-19 15:47:47.878138
107	openai	NOT_CONFIGURED	\N	2026-08-19 15:47:47.879137
108	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:47:47.879137
109	simulation	HEALTHY	\N	2026-08-19 15:47:47.879137
110	application	HEALTHY	4.5	2026-08-19 15:47:47.879137
111	database	HEALTHY	0	2026-08-19 15:48:17.938924
112	redis	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
113	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
114	celery	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
115	email	HEALTHY	\N	2026-08-19 15:48:17.938924
116	backup	DEGRADED	\N	2026-08-19 15:48:17.938924
117	sentry	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
118	openai	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
119	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:48:17.938924
120	simulation	HEALTHY	\N	2026-08-19 15:48:17.938924
121	application	HEALTHY	4.5	2026-08-19 15:48:17.938924
122	database	HEALTHY	0	2026-08-19 15:48:47.970409
123	redis	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
124	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
125	celery	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
126	email	HEALTHY	\N	2026-08-19 15:48:47.970409
127	backup	DEGRADED	\N	2026-08-19 15:48:47.970409
128	sentry	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
129	openai	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
130	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:48:47.970409
131	simulation	HEALTHY	\N	2026-08-19 15:48:47.970409
132	application	HEALTHY	4.5	2026-08-19 15:48:47.970409
133	database	HEALTHY	0	2026-08-19 15:49:18.017824
134	redis	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
135	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
136	celery	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
137	email	HEALTHY	\N	2026-08-19 15:49:18.017824
138	backup	DEGRADED	\N	2026-08-19 15:49:18.017824
139	sentry	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
140	openai	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
141	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:49:18.017824
142	simulation	HEALTHY	\N	2026-08-19 15:49:18.017824
143	application	HEALTHY	4.5	2026-08-19 15:49:18.017824
144	database	HEALTHY	0	2026-08-19 15:49:48.067227
145	redis	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
146	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
147	celery	NOT_CONFIGURED	\N	2026-08-19 15:49:48.067227
148	email	HEALTHY	\N	2026-08-19 15:49:48.067227
149	backup	DEGRADED	\N	2026-08-19 15:49:48.068228
150	sentry	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
151	openai	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
152	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:49:48.068228
153	simulation	HEALTHY	\N	2026-08-19 15:49:48.068228
154	application	HEALTHY	4.5	2026-08-19 15:49:48.068228
155	database	HEALTHY	0	2026-08-19 15:50:18.108276
156	redis	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
157	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
158	celery	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
159	email	HEALTHY	\N	2026-08-19 15:50:18.109288
160	backup	DEGRADED	\N	2026-08-19 15:50:18.109288
161	sentry	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
162	openai	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
163	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:50:18.109288
164	simulation	HEALTHY	\N	2026-08-19 15:50:18.109288
165	application	HEALTHY	4.5	2026-08-19 15:50:18.109288
166	database	HEALTHY	0	2026-08-19 15:50:48.141889
167	redis	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
168	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
169	celery	NOT_CONFIGURED	\N	2026-08-19 15:50:48.141889
170	email	HEALTHY	\N	2026-08-19 15:50:48.141889
171	backup	DEGRADED	\N	2026-08-19 15:50:48.141889
172	sentry	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
173	openai	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
174	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:50:48.143248
175	simulation	HEALTHY	\N	2026-08-19 15:50:48.143248
176	application	HEALTHY	4.5	2026-08-19 15:50:48.143248
177	database	HEALTHY	0	2026-08-19 15:51:18.179254
178	redis	NOT_CONFIGURED	\N	2026-08-19 15:51:18.179254
179	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:51:18.179254
180	celery	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
181	email	HEALTHY	\N	2026-08-19 15:51:18.180254
182	backup	DEGRADED	\N	2026-08-19 15:51:18.180254
183	sentry	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
184	openai	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
185	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:51:18.180254
186	simulation	HEALTHY	\N	2026-08-19 15:51:18.180254
187	application	HEALTHY	4.5	2026-08-19 15:51:18.180254
188	database	HEALTHY	0.69	2026-08-19 15:51:48.208362
189	redis	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
190	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
191	celery	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
192	email	HEALTHY	\N	2026-08-19 15:51:48.208362
193	backup	DEGRADED	\N	2026-08-19 15:51:48.208362
194	sentry	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
195	openai	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
196	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:51:48.208362
197	simulation	HEALTHY	\N	2026-08-19 15:51:48.208362
198	application	HEALTHY	4.5	2026-08-19 15:51:48.208362
199	database	HEALTHY	1.02	2026-08-19 15:52:18.241292
200	redis	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
201	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
202	celery	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
203	email	HEALTHY	\N	2026-08-19 15:52:18.242297
204	backup	DEGRADED	\N	2026-08-19 15:52:18.242297
205	sentry	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
206	openai	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
207	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:52:18.242297
208	simulation	HEALTHY	\N	2026-08-19 15:52:18.242297
209	application	HEALTHY	4.5	2026-08-19 15:52:18.242297
210	database	HEALTHY	1	2026-08-19 15:52:48.278019
211	redis	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
212	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
213	celery	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
214	email	HEALTHY	\N	2026-08-19 15:52:48.279014
215	backup	DEGRADED	\N	2026-08-19 15:52:48.279014
216	sentry	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
217	openai	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
218	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:52:48.279014
219	simulation	HEALTHY	\N	2026-08-19 15:52:48.279014
220	application	HEALTHY	4.5	2026-08-19 15:52:48.279014
221	database	HEALTHY	1	2026-08-19 15:53:18.310184
222	redis	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
223	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
224	celery	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
225	email	HEALTHY	\N	2026-08-19 15:53:18.310184
226	backup	DEGRADED	\N	2026-08-19 15:53:18.310184
227	sentry	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
228	openai	NOT_CONFIGURED	\N	2026-08-19 15:53:18.310184
229	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:53:18.311185
230	simulation	HEALTHY	\N	2026-08-19 15:53:18.311185
231	application	HEALTHY	4.5	2026-08-19 15:53:18.311185
232	database	HEALTHY	1.05	2026-08-19 15:53:48.350893
233	redis	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
234	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
235	celery	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
236	email	HEALTHY	\N	2026-08-19 15:53:48.350893
237	backup	DEGRADED	\N	2026-08-19 15:53:48.350893
238	sentry	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
239	openai	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
240	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:53:48.350893
241	simulation	HEALTHY	\N	2026-08-19 15:53:48.350893
242	application	HEALTHY	4.5	2026-08-19 15:53:48.350893
243	database	HEALTHY	0	2026-08-19 15:54:18.38665
244	redis	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
245	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
246	celery	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
247	email	HEALTHY	\N	2026-08-19 15:54:18.38665
248	backup	DEGRADED	\N	2026-08-19 15:54:18.38665
249	sentry	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
250	openai	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
251	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:54:18.38665
252	simulation	HEALTHY	\N	2026-08-19 15:54:18.38665
253	application	HEALTHY	4.5	2026-08-19 15:54:18.38665
254	database	HEALTHY	0	2026-08-19 15:54:48.415246
255	redis	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
256	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
257	celery	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
258	email	HEALTHY	\N	2026-08-19 15:54:48.415246
259	backup	DEGRADED	\N	2026-08-19 15:54:48.415246
260	sentry	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
261	openai	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
262	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:54:48.415246
263	simulation	HEALTHY	\N	2026-08-19 15:54:48.415246
264	application	HEALTHY	4.5	2026-08-19 15:54:48.415246
265	database	HEALTHY	1	2026-08-19 15:55:18.447024
266	redis	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
267	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
268	celery	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
269	email	HEALTHY	\N	2026-08-19 15:55:18.448023
270	backup	DEGRADED	\N	2026-08-19 15:55:18.448023
271	sentry	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
272	openai	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
273	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:55:18.448023
274	simulation	HEALTHY	\N	2026-08-19 15:55:18.448023
275	application	HEALTHY	4.5	2026-08-19 15:55:18.448023
276	database	HEALTHY	0	2026-08-19 15:55:48.482337
277	redis	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
278	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
279	celery	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
280	email	HEALTHY	\N	2026-08-19 15:55:48.482337
281	backup	DEGRADED	\N	2026-08-19 15:55:48.482337
282	sentry	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
283	openai	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
284	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:55:48.482337
285	simulation	HEALTHY	\N	2026-08-19 15:55:48.482337
286	application	HEALTHY	4.5	2026-08-19 15:55:48.482337
287	database	HEALTHY	1.66	2026-08-19 15:56:18.648095
288	redis	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
289	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
290	celery	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
291	email	HEALTHY	\N	2026-08-19 15:56:18.648095
292	backup	DEGRADED	\N	2026-08-19 15:56:18.648095
293	sentry	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
294	openai	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
295	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:56:18.648095
296	simulation	HEALTHY	\N	2026-08-19 15:56:18.648095
297	application	HEALTHY	4.5	2026-08-19 15:56:18.648095
298	database	HEALTHY	0	2026-08-19 15:56:48.675899
299	redis	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
300	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
301	celery	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
302	email	HEALTHY	\N	2026-08-19 15:56:48.675899
303	backup	DEGRADED	\N	2026-08-19 15:56:48.675899
304	sentry	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
305	openai	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
306	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:56:48.675899
307	simulation	HEALTHY	\N	2026-08-19 15:56:48.675899
308	application	HEALTHY	4.5	2026-08-19 15:56:48.675899
309	database	HEALTHY	0	2026-08-19 15:57:18.709025
310	redis	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
311	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
312	celery	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
313	email	HEALTHY	\N	2026-08-19 15:57:18.710392
314	backup	DEGRADED	\N	2026-08-19 15:57:18.710392
315	sentry	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
316	openai	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
317	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:57:18.710392
318	simulation	HEALTHY	\N	2026-08-19 15:57:18.710392
319	application	HEALTHY	4.5	2026-08-19 15:57:18.710392
320	database	HEALTHY	0.51	2026-08-19 15:57:48.749251
321	redis	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
322	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
323	celery	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
324	email	HEALTHY	\N	2026-08-19 15:57:48.750811
325	backup	DEGRADED	\N	2026-08-19 15:57:48.750811
326	sentry	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
327	openai	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
328	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:57:48.750811
329	simulation	HEALTHY	\N	2026-08-19 15:57:48.750811
330	application	HEALTHY	4.5	2026-08-19 15:57:48.750811
331	database	HEALTHY	0	2026-08-19 15:58:18.775742
332	redis	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
333	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
334	celery	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
335	email	HEALTHY	\N	2026-08-19 15:58:18.775742
336	backup	DEGRADED	\N	2026-08-19 15:58:18.775742
337	sentry	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
338	openai	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
339	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:58:18.775742
340	simulation	HEALTHY	\N	2026-08-19 15:58:18.775742
341	application	HEALTHY	4.5	2026-08-19 15:58:18.776745
342	database	HEALTHY	1	2026-08-19 15:58:48.839837
343	redis	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
344	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
345	celery	NOT_CONFIGURED	\N	2026-08-19 15:58:48.839837
346	email	HEALTHY	\N	2026-08-19 15:58:48.839837
347	backup	DEGRADED	\N	2026-08-19 15:58:48.839837
348	sentry	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
349	openai	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
350	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:58:48.840835
351	simulation	HEALTHY	\N	2026-08-19 15:58:48.840835
352	application	HEALTHY	4.5	2026-08-19 15:58:48.840835
353	database	HEALTHY	0	2026-08-19 15:59:18.887093
354	redis	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
355	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
356	celery	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
357	email	HEALTHY	\N	2026-08-19 15:59:18.887093
358	backup	DEGRADED	\N	2026-08-19 15:59:18.887093
359	sentry	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
360	openai	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
361	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:59:18.887093
362	simulation	HEALTHY	\N	2026-08-19 15:59:18.887093
363	application	HEALTHY	4.5	2026-08-19 15:59:18.887093
364	database	HEALTHY	2	2026-08-19 15:59:48.921252
365	redis	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
366	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
367	celery	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
368	email	HEALTHY	\N	2026-08-19 15:59:48.922252
369	backup	DEGRADED	\N	2026-08-19 15:59:48.922252
370	sentry	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
371	openai	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
372	cloudflare	NOT_CONFIGURED	\N	2026-08-19 15:59:48.922252
373	simulation	HEALTHY	\N	2026-08-19 15:59:48.922252
374	application	HEALTHY	4.5	2026-08-19 15:59:48.922252
375	database	HEALTHY	0.72	2026-08-19 16:00:18.986965
376	redis	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
377	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
378	celery	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
379	email	HEALTHY	\N	2026-08-19 16:00:18.986965
380	backup	DEGRADED	\N	2026-08-19 16:00:18.986965
381	sentry	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
382	openai	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
383	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:00:18.986965
384	simulation	HEALTHY	\N	2026-08-19 16:00:18.986965
385	application	HEALTHY	4.5	2026-08-19 16:00:18.986965
386	database	HEALTHY	0	2026-08-19 16:00:49.058315
387	redis	NOT_CONFIGURED	\N	2026-08-19 16:00:49.058315
388	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
389	celery	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
390	email	HEALTHY	\N	2026-08-19 16:00:49.059309
391	backup	DEGRADED	\N	2026-08-19 16:00:49.059309
392	sentry	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
393	openai	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
394	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:00:49.059309
395	simulation	HEALTHY	\N	2026-08-19 16:00:49.059309
396	application	HEALTHY	4.5	2026-08-19 16:00:49.059309
397	database	HEALTHY	0.99	2026-08-19 16:01:19.090784
398	redis	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
399	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
400	celery	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
401	email	HEALTHY	\N	2026-08-19 16:01:19.090784
402	backup	DEGRADED	\N	2026-08-19 16:01:19.090784
403	sentry	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
404	openai	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
405	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:01:19.090784
406	simulation	HEALTHY	\N	2026-08-19 16:01:19.090784
407	application	HEALTHY	4.5	2026-08-19 16:01:19.090784
408	database	HEALTHY	1	2026-08-19 16:01:49.238816
409	redis	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
410	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
411	celery	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
412	email	HEALTHY	\N	2026-08-19 16:01:49.238816
413	backup	DEGRADED	\N	2026-08-19 16:01:49.238816
414	sentry	NOT_CONFIGURED	\N	2026-08-19 16:01:49.238816
415	openai	NOT_CONFIGURED	\N	2026-08-19 16:01:49.239799
416	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:01:49.239799
417	simulation	HEALTHY	\N	2026-08-19 16:01:49.239799
418	application	HEALTHY	4.5	2026-08-19 16:01:49.239799
419	database	HEALTHY	1	2026-08-19 16:02:19.277167
420	redis	NOT_CONFIGURED	\N	2026-08-19 16:02:19.277167
421	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:02:19.277167
422	celery	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
423	email	HEALTHY	\N	2026-08-19 16:02:19.278171
424	backup	DEGRADED	\N	2026-08-19 16:02:19.278171
425	sentry	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
426	openai	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
427	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:02:19.278171
428	simulation	HEALTHY	\N	2026-08-19 16:02:19.278171
429	application	HEALTHY	4.5	2026-08-19 16:02:19.278171
430	database	HEALTHY	0	2026-08-19 16:02:49.309146
431	redis	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
432	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
433	celery	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
434	email	HEALTHY	\N	2026-08-19 16:02:49.309146
435	backup	DEGRADED	\N	2026-08-19 16:02:49.309146
436	sentry	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
437	openai	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
438	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:02:49.309146
439	simulation	HEALTHY	\N	2026-08-19 16:02:49.309146
440	application	HEALTHY	4.5	2026-08-19 16:02:49.309146
441	database	HEALTHY	0	2026-08-19 16:03:19.347408
442	redis	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
443	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
444	celery	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
445	email	HEALTHY	\N	2026-08-19 16:03:19.348405
446	backup	DEGRADED	\N	2026-08-19 16:03:19.348405
447	sentry	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
448	openai	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
449	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:03:19.348405
450	simulation	HEALTHY	\N	2026-08-19 16:03:19.348405
451	application	HEALTHY	4.5	2026-08-19 16:03:19.348405
452	database	HEALTHY	0	2026-08-19 16:03:49.394343
453	redis	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
454	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
455	celery	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
456	email	HEALTHY	\N	2026-08-19 16:03:49.394343
457	backup	DEGRADED	\N	2026-08-19 16:03:49.394343
458	sentry	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
459	openai	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
460	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:03:49.394343
461	simulation	HEALTHY	\N	2026-08-19 16:03:49.394343
462	application	HEALTHY	4.5	2026-08-19 16:03:49.394343
463	database	HEALTHY	1	2026-08-19 16:04:19.434344
464	redis	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
465	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
466	celery	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
467	email	HEALTHY	\N	2026-08-19 16:04:19.43532
468	backup	DEGRADED	\N	2026-08-19 16:04:19.43532
469	sentry	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
470	openai	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
471	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:04:19.43532
472	simulation	HEALTHY	\N	2026-08-19 16:04:19.43532
473	application	HEALTHY	4.5	2026-08-19 16:04:19.43532
474	database	HEALTHY	0	2026-08-19 16:04:49.498861
475	redis	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
476	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
477	celery	NOT_CONFIGURED	\N	2026-08-19 16:04:49.498861
478	email	HEALTHY	\N	2026-08-19 16:04:49.499858
479	backup	DEGRADED	\N	2026-08-19 16:04:49.499858
480	sentry	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
481	openai	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
482	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:04:49.499858
483	simulation	HEALTHY	\N	2026-08-19 16:04:49.499858
484	application	HEALTHY	4.5	2026-08-19 16:04:49.499858
485	database	HEALTHY	0	2026-08-19 16:05:19.529283
486	redis	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
487	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
488	celery	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
489	email	HEALTHY	\N	2026-08-19 16:05:19.529283
490	backup	DEGRADED	\N	2026-08-19 16:05:19.529283
491	sentry	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
492	openai	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
493	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:05:19.529283
494	simulation	HEALTHY	\N	2026-08-19 16:05:19.529283
495	application	HEALTHY	4.5	2026-08-19 16:05:19.529283
496	database	HEALTHY	1	2026-08-19 16:05:49.581173
497	redis	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
498	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
499	celery	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
500	email	HEALTHY	\N	2026-08-19 16:05:49.581173
501	backup	DEGRADED	\N	2026-08-19 16:05:49.581173
502	sentry	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
503	openai	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
504	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:05:49.581173
505	simulation	HEALTHY	\N	2026-08-19 16:05:49.581173
506	application	HEALTHY	4.5	2026-08-19 16:05:49.581173
507	database	HEALTHY	1	2026-08-19 16:06:19.623269
508	redis	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
509	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
510	celery	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
511	email	HEALTHY	\N	2026-08-19 16:06:19.623269
512	backup	DEGRADED	\N	2026-08-19 16:06:19.623269
513	sentry	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
514	openai	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
515	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:06:19.623269
516	simulation	HEALTHY	\N	2026-08-19 16:06:19.623269
517	application	HEALTHY	4.5	2026-08-19 16:06:19.623269
518	database	HEALTHY	0	2026-08-19 16:06:49.655565
519	redis	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
520	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
521	celery	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
522	email	HEALTHY	\N	2026-08-19 16:06:49.656561
523	backup	DEGRADED	\N	2026-08-19 16:06:49.656561
524	sentry	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
525	openai	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
526	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:06:49.656561
527	simulation	HEALTHY	\N	2026-08-19 16:06:49.656561
528	application	HEALTHY	4.5	2026-08-19 16:06:49.656561
529	database	HEALTHY	0	2026-08-19 16:07:19.686925
530	redis	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
531	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
532	celery	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
533	email	HEALTHY	\N	2026-08-19 16:07:19.687925
534	backup	DEGRADED	\N	2026-08-19 16:07:19.687925
535	sentry	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
536	openai	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
537	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:07:19.687925
538	simulation	HEALTHY	\N	2026-08-19 16:07:19.687925
539	application	HEALTHY	4.5	2026-08-19 16:07:19.687925
540	database	HEALTHY	1	2026-08-19 16:07:49.742458
541	redis	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
542	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
543	celery	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
544	email	HEALTHY	\N	2026-08-19 16:07:49.743901
545	backup	DEGRADED	\N	2026-08-19 16:07:49.743901
546	sentry	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
547	openai	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
548	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:07:49.743901
549	simulation	HEALTHY	\N	2026-08-19 16:07:49.743901
550	application	HEALTHY	4.5	2026-08-19 16:07:49.743901
551	database	HEALTHY	0	2026-08-19 16:08:19.773555
552	redis	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
553	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
554	celery	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
555	email	HEALTHY	\N	2026-08-19 16:08:19.773555
556	backup	DEGRADED	\N	2026-08-19 16:08:19.773555
557	sentry	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
558	openai	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
559	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:08:19.773555
560	simulation	HEALTHY	\N	2026-08-19 16:08:19.773555
561	application	HEALTHY	4.5	2026-08-19 16:08:19.773555
1233	database	HEALTHY	1	2026-08-19 16:39:22.761803
1234	redis	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1235	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1236	celery	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1237	email	HEALTHY	\N	2026-08-19 16:39:22.761803
1238	backup	UNAVAILABLE	\N	2026-08-19 16:39:22.761803
1239	sentry	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1240	openai	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1241	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:39:22.761803
1242	simulation	HEALTHY	\N	2026-08-19 16:39:22.761803
1243	application	HEALTHY	4.5	2026-08-19 16:39:22.761803
1354	database	HEALTHY	8.02	2026-08-19 16:44:53.645413
1355	redis	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1356	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1357	celery	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1358	email	HEALTHY	\N	2026-08-19 16:44:53.646429
1359	backup	UNAVAILABLE	\N	2026-08-19 16:44:53.646429
1360	sentry	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1361	openai	NOT_CONFIGURED	\N	2026-08-19 16:44:53.646429
1362	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:44:53.64743
1363	simulation	HEALTHY	\N	2026-08-19 16:44:53.64743
1364	application	HEALTHY	4.5	2026-08-19 16:44:53.64743
1409	database	HEALTHY	1.01	2026-08-19 16:47:23.877649
1410	redis	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1411	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1412	celery	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1413	email	HEALTHY	\N	2026-08-19 16:47:23.877649
1414	backup	UNAVAILABLE	\N	2026-08-19 16:47:23.877649
1415	sentry	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1416	openai	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1417	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:47:23.877649
1418	simulation	HEALTHY	\N	2026-08-19 16:47:23.87865
1419	application	HEALTHY	4.5	2026-08-19 16:47:23.87865
1453	database	HEALTHY	0	2026-08-19 16:49:24.035361
1454	redis	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1455	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1456	celery	NOT_CONFIGURED	\N	2026-08-19 16:49:24.035361
1457	email	HEALTHY	\N	2026-08-19 16:49:24.035361
1458	backup	UNAVAILABLE	\N	2026-08-19 16:49:24.036359
1459	sentry	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1460	openai	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1461	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:49:24.036359
1462	simulation	HEALTHY	\N	2026-08-19 16:49:24.036359
1463	application	HEALTHY	4.5	2026-08-19 16:49:24.036359
1508	database	HEALTHY	4.99	2026-08-19 16:51:54.281725
1509	redis	NOT_CONFIGURED	\N	2026-08-19 16:51:54.281725
1510	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:51:54.281725
1511	celery	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1512	email	HEALTHY	\N	2026-08-19 16:51:54.282728
1513	backup	UNAVAILABLE	\N	2026-08-19 16:51:54.282728
1514	sentry	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1515	openai	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1516	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:51:54.282728
1517	simulation	HEALTHY	\N	2026-08-19 16:51:54.282728
1518	application	HEALTHY	4.5	2026-08-19 16:51:54.282728
1574	database	HEALTHY	1.08	2026-08-19 16:54:54.524623
1575	redis	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1576	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1577	celery	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
562	database	HEALTHY	0	2026-08-19 16:08:49.807318
563	redis	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
564	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
565	celery	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
566	email	HEALTHY	\N	2026-08-19 16:08:49.807318
567	backup	DEGRADED	\N	2026-08-19 16:08:49.807318
568	sentry	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
569	openai	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
570	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:08:49.807318
571	simulation	HEALTHY	\N	2026-08-19 16:08:49.807318
572	application	HEALTHY	4.5	2026-08-19 16:08:49.807318
573	database	HEALTHY	0.97	2026-08-19 16:09:19.84777
574	redis	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
575	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
576	celery	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
577	email	HEALTHY	\N	2026-08-19 16:09:19.84777
578	backup	DEGRADED	\N	2026-08-19 16:09:19.84777
579	sentry	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
580	openai	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
581	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:09:19.84777
582	simulation	HEALTHY	\N	2026-08-19 16:09:19.84777
583	application	HEALTHY	4.5	2026-08-19 16:09:19.84777
584	database	HEALTHY	1	2026-08-19 16:09:49.883057
585	redis	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
586	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
587	celery	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
588	email	HEALTHY	\N	2026-08-19 16:09:49.883057
589	backup	DEGRADED	\N	2026-08-19 16:09:49.883057
590	sentry	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
591	openai	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
592	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:09:49.883057
593	simulation	HEALTHY	\N	2026-08-19 16:09:49.883057
594	application	HEALTHY	4.5	2026-08-19 16:09:49.883057
595	database	HEALTHY	1	2026-08-19 16:10:19.927704
596	redis	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
597	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
598	celery	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
599	email	HEALTHY	\N	2026-08-19 16:10:19.927704
600	backup	DEGRADED	\N	2026-08-19 16:10:19.927704
601	sentry	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
602	openai	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
603	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:10:19.927704
604	simulation	HEALTHY	\N	2026-08-19 16:10:19.927704
605	application	HEALTHY	4.5	2026-08-19 16:10:19.927704
606	database	HEALTHY	0	2026-08-19 16:10:49.9668
607	redis	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
608	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
609	celery	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
610	email	HEALTHY	\N	2026-08-19 16:10:49.9668
611	backup	DEGRADED	\N	2026-08-19 16:10:49.9668
612	sentry	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
613	openai	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
614	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:10:49.9668
615	simulation	HEALTHY	\N	2026-08-19 16:10:49.9668
616	application	HEALTHY	4.5	2026-08-19 16:10:49.9668
617	database	HEALTHY	0	2026-08-19 16:11:20.002192
618	redis	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
619	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
620	celery	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
621	email	HEALTHY	\N	2026-08-19 16:11:20.002192
622	backup	DEGRADED	\N	2026-08-19 16:11:20.002192
623	sentry	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
624	openai	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
625	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:11:20.002192
626	simulation	HEALTHY	\N	2026-08-19 16:11:20.002192
627	application	HEALTHY	4.5	2026-08-19 16:11:20.002192
628	database	HEALTHY	0	2026-08-19 16:11:50.04983
629	redis	NOT_CONFIGURED	\N	2026-08-19 16:11:50.04983
630	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:11:50.04983
631	celery	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
632	email	HEALTHY	\N	2026-08-19 16:11:50.050895
633	backup	DEGRADED	\N	2026-08-19 16:11:50.050895
634	sentry	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
635	openai	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
636	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:11:50.050895
637	simulation	HEALTHY	\N	2026-08-19 16:11:50.050895
638	application	HEALTHY	4.5	2026-08-19 16:11:50.050895
639	database	HEALTHY	1	2026-08-19 16:12:20.079732
640	redis	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
641	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
642	celery	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
643	email	HEALTHY	\N	2026-08-19 16:12:20.079732
644	backup	DEGRADED	\N	2026-08-19 16:12:20.079732
645	sentry	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
646	openai	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
647	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:12:20.079732
648	simulation	HEALTHY	\N	2026-08-19 16:12:20.079732
649	application	HEALTHY	4.5	2026-08-19 16:12:20.079732
650	database	HEALTHY	0	2026-08-19 16:12:50.133789
651	redis	NOT_CONFIGURED	\N	2026-08-19 16:12:50.133789
652	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
653	celery	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
654	email	HEALTHY	\N	2026-08-19 16:12:50.135114
655	backup	DEGRADED	\N	2026-08-19 16:12:50.135114
656	sentry	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
657	openai	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
658	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:12:50.135114
659	simulation	HEALTHY	\N	2026-08-19 16:12:50.135114
660	application	HEALTHY	4.5	2026-08-19 16:12:50.135114
661	database	HEALTHY	3	2026-08-19 16:13:20.207174
662	redis	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
663	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
664	celery	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
665	email	HEALTHY	\N	2026-08-19 16:13:20.207174
666	backup	DEGRADED	\N	2026-08-19 16:13:20.207174
667	sentry	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
668	openai	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
669	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:13:20.207174
670	simulation	HEALTHY	\N	2026-08-19 16:13:20.208717
671	application	HEALTHY	4.5	2026-08-19 16:13:20.208717
672	database	HEALTHY	3.99	2026-08-19 16:13:50.405009
673	redis	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
674	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
675	celery	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
676	email	HEALTHY	\N	2026-08-19 16:13:50.40601
677	backup	DEGRADED	\N	2026-08-19 16:13:50.40601
678	sentry	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
679	openai	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
680	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:13:50.40601
681	simulation	HEALTHY	\N	2026-08-19 16:13:50.40601
682	application	HEALTHY	4.5	2026-08-19 16:13:50.40601
683	database	HEALTHY	0	2026-08-19 16:14:20.625927
684	redis	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
685	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
686	celery	NOT_CONFIGURED	\N	2026-08-19 16:14:20.625927
687	email	HEALTHY	\N	2026-08-19 16:14:20.626928
688	backup	DEGRADED	\N	2026-08-19 16:14:20.626928
689	sentry	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
690	openai	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
691	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:14:20.626928
692	simulation	HEALTHY	\N	2026-08-19 16:14:20.626928
693	application	HEALTHY	4.5	2026-08-19 16:14:20.626928
694	database	HEALTHY	0.99	2026-08-19 16:14:50.668735
695	redis	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
696	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
697	celery	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
698	email	HEALTHY	\N	2026-08-19 16:14:50.668735
699	backup	DEGRADED	\N	2026-08-19 16:14:50.668735
700	sentry	NOT_CONFIGURED	\N	2026-08-19 16:14:50.668735
701	openai	NOT_CONFIGURED	\N	2026-08-19 16:14:50.669736
702	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:14:50.669736
703	simulation	HEALTHY	\N	2026-08-19 16:14:50.669736
704	application	HEALTHY	4.5	2026-08-19 16:14:50.669736
705	database	HEALTHY	1.01	2026-08-19 16:15:20.70198
706	redis	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
707	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
708	celery	NOT_CONFIGURED	\N	2026-08-19 16:15:20.70198
709	email	HEALTHY	\N	2026-08-19 16:15:20.70198
710	backup	DEGRADED	\N	2026-08-19 16:15:20.702983
711	sentry	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
712	openai	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
713	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:15:20.702983
714	simulation	HEALTHY	\N	2026-08-19 16:15:20.702983
715	application	HEALTHY	4.5	2026-08-19 16:15:20.702983
716	database	HEALTHY	1.02	2026-08-19 16:15:50.762278
717	redis	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
718	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
719	celery	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
720	email	HEALTHY	\N	2026-08-19 16:15:50.762278
721	backup	DEGRADED	\N	2026-08-19 16:15:50.762278
722	sentry	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
723	openai	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
724	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:15:50.762278
725	simulation	HEALTHY	\N	2026-08-19 16:15:50.762278
726	application	HEALTHY	4.5	2026-08-19 16:15:50.762278
727	database	HEALTHY	0	2026-08-19 16:16:20.807288
728	redis	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
729	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
730	celery	NOT_CONFIGURED	\N	2026-08-19 16:16:20.807288
731	email	HEALTHY	\N	2026-08-19 16:16:20.808291
732	backup	DEGRADED	\N	2026-08-19 16:16:20.808291
733	sentry	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
734	openai	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
735	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:16:20.808291
736	simulation	HEALTHY	\N	2026-08-19 16:16:20.808291
737	application	HEALTHY	4.5	2026-08-19 16:16:20.808291
738	database	HEALTHY	1	2026-08-19 16:16:50.86567
739	redis	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
740	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
741	celery	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
742	email	HEALTHY	\N	2026-08-19 16:16:50.86567
743	backup	DEGRADED	\N	2026-08-19 16:16:50.86567
744	sentry	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
745	openai	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
746	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:16:50.86567
747	simulation	HEALTHY	\N	2026-08-19 16:16:50.86567
748	application	HEALTHY	4.5	2026-08-19 16:16:50.86567
749	database	HEALTHY	0	2026-08-19 16:17:20.900338
750	redis	NOT_CONFIGURED	\N	2026-08-19 16:17:20.900338
751	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
752	celery	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
753	email	HEALTHY	\N	2026-08-19 16:17:20.901367
754	backup	DEGRADED	\N	2026-08-19 16:17:20.901367
755	sentry	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
756	openai	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
757	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:17:20.901367
758	simulation	HEALTHY	\N	2026-08-19 16:17:20.901367
759	application	HEALTHY	4.5	2026-08-19 16:17:20.901367
760	database	HEALTHY	0.99	2026-08-19 16:17:50.958135
761	redis	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
762	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
763	celery	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
764	email	HEALTHY	\N	2026-08-19 16:17:50.958135
765	backup	DEGRADED	\N	2026-08-19 16:17:50.958135
766	sentry	NOT_CONFIGURED	\N	2026-08-19 16:17:50.958135
767	openai	NOT_CONFIGURED	\N	2026-08-19 16:17:50.959133
768	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:17:50.959133
769	simulation	HEALTHY	\N	2026-08-19 16:17:50.959133
770	application	HEALTHY	4.5	2026-08-19 16:17:50.959133
771	database	HEALTHY	0	2026-08-19 16:18:20.992804
772	redis	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
773	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
774	celery	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
775	email	HEALTHY	\N	2026-08-19 16:18:20.993803
776	backup	DEGRADED	\N	2026-08-19 16:18:20.993803
777	sentry	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
778	openai	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
779	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:18:20.993803
780	simulation	HEALTHY	\N	2026-08-19 16:18:20.993803
781	application	HEALTHY	4.5	2026-08-19 16:18:20.993803
782	database	HEALTHY	0	2026-08-19 16:18:51.042369
783	redis	NOT_CONFIGURED	\N	2026-08-19 16:18:51.042369
784	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
785	celery	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
786	email	HEALTHY	\N	2026-08-19 16:18:51.043367
787	backup	DEGRADED	\N	2026-08-19 16:18:51.043367
788	sentry	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
789	openai	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
790	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:18:51.043367
791	simulation	HEALTHY	\N	2026-08-19 16:18:51.043367
792	application	HEALTHY	4.5	2026-08-19 16:18:51.043367
793	database	HEALTHY	0	2026-08-19 16:19:21.075709
794	redis	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
795	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
796	celery	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
797	email	HEALTHY	\N	2026-08-19 16:19:21.075709
798	backup	DEGRADED	\N	2026-08-19 16:19:21.075709
799	sentry	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
800	openai	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
801	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:19:21.075709
802	simulation	HEALTHY	\N	2026-08-19 16:19:21.075709
803	application	HEALTHY	4.5	2026-08-19 16:19:21.075709
804	database	HEALTHY	0	2026-08-19 16:19:51.108704
805	redis	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
806	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
807	celery	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
808	email	HEALTHY	\N	2026-08-19 16:19:51.108704
809	backup	DEGRADED	\N	2026-08-19 16:19:51.108704
810	sentry	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
811	openai	NOT_CONFIGURED	\N	2026-08-19 16:19:51.108704
812	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:19:51.109691
813	simulation	HEALTHY	\N	2026-08-19 16:19:51.109691
814	application	HEALTHY	4.5	2026-08-19 16:19:51.109691
815	database	HEALTHY	1	2026-08-19 16:20:21.135138
816	redis	NOT_CONFIGURED	\N	2026-08-19 16:20:21.135138
817	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
818	celery	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
819	email	HEALTHY	\N	2026-08-19 16:20:21.136481
820	backup	DEGRADED	\N	2026-08-19 16:20:21.136481
821	sentry	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
822	openai	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
823	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:20:21.136481
824	simulation	HEALTHY	\N	2026-08-19 16:20:21.136481
825	application	HEALTHY	4.5	2026-08-19 16:20:21.136481
826	database	HEALTHY	0.99	2026-08-19 16:20:51.174426
827	redis	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
828	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
829	celery	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
830	email	HEALTHY	\N	2026-08-19 16:20:51.174426
831	backup	DEGRADED	\N	2026-08-19 16:20:51.174426
832	sentry	NOT_CONFIGURED	\N	2026-08-19 16:20:51.174426
833	openai	NOT_CONFIGURED	\N	2026-08-19 16:20:51.175438
834	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:20:51.175438
835	simulation	HEALTHY	\N	2026-08-19 16:20:51.175438
836	application	HEALTHY	4.5	2026-08-19 16:20:51.175438
837	database	HEALTHY	1	2026-08-19 16:21:21.215392
838	redis	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
839	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
840	celery	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
841	email	HEALTHY	\N	2026-08-19 16:21:21.216392
842	backup	DEGRADED	\N	2026-08-19 16:21:21.216392
843	sentry	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
844	openai	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
845	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:21:21.216392
846	simulation	HEALTHY	\N	2026-08-19 16:21:21.216392
847	application	HEALTHY	4.5	2026-08-19 16:21:21.216392
848	database	HEALTHY	0	2026-08-19 16:21:51.250566
849	redis	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
850	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
851	celery	NOT_CONFIGURED	\N	2026-08-19 16:21:51.250566
852	email	HEALTHY	\N	2026-08-19 16:21:51.250566
853	backup	DEGRADED	\N	2026-08-19 16:21:51.252337
854	sentry	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
855	openai	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
856	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:21:51.252337
857	simulation	HEALTHY	\N	2026-08-19 16:21:51.252337
858	application	HEALTHY	4.5	2026-08-19 16:21:51.252337
859	database	HEALTHY	0.99	2026-08-19 16:22:21.278654
860	redis	NOT_CONFIGURED	\N	2026-08-19 16:22:21.278654
861	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:22:21.278654
862	celery	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
863	email	HEALTHY	\N	2026-08-19 16:22:21.279694
864	backup	DEGRADED	\N	2026-08-19 16:22:21.279694
865	sentry	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
866	openai	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
867	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:22:21.279694
868	simulation	HEALTHY	\N	2026-08-19 16:22:21.279694
869	application	HEALTHY	4.5	2026-08-19 16:22:21.279694
870	database	HEALTHY	1	2026-08-19 16:22:51.337485
871	redis	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
872	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
873	celery	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
874	email	HEALTHY	\N	2026-08-19 16:22:51.337485
875	backup	DEGRADED	\N	2026-08-19 16:22:51.337485
876	sentry	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
877	openai	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
878	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:22:51.337485
879	simulation	HEALTHY	\N	2026-08-19 16:22:51.337485
880	application	HEALTHY	4.5	2026-08-19 16:22:51.337485
881	database	HEALTHY	0	2026-08-19 16:23:21.363007
882	redis	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
883	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
884	celery	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
885	email	HEALTHY	\N	2026-08-19 16:23:21.363007
886	backup	DEGRADED	\N	2026-08-19 16:23:21.363007
887	sentry	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
888	openai	NOT_CONFIGURED	\N	2026-08-19 16:23:21.363007
889	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:23:21.364007
890	simulation	HEALTHY	\N	2026-08-19 16:23:21.364007
891	application	HEALTHY	4.5	2026-08-19 16:23:21.364007
892	database	HEALTHY	1	2026-08-19 16:23:51.414808
893	redis	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
894	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
895	celery	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
896	email	HEALTHY	\N	2026-08-19 16:23:51.415804
897	backup	HEALTHY	\N	2026-08-19 16:23:51.415804
898	sentry	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
899	openai	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
900	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:23:51.415804
901	simulation	HEALTHY	\N	2026-08-19 16:23:51.415804
902	application	HEALTHY	4.5	2026-08-19 16:23:51.415804
903	database	HEALTHY	1.48	2026-08-19 16:24:21.444658
904	redis	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
905	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
906	celery	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
907	email	HEALTHY	\N	2026-08-19 16:24:21.446061
908	backup	UNAVAILABLE	\N	2026-08-19 16:24:21.446061
909	sentry	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
910	openai	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
911	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:24:21.446061
912	simulation	HEALTHY	\N	2026-08-19 16:24:21.446061
913	application	HEALTHY	4.5	2026-08-19 16:24:21.446061
914	database	HEALTHY	1	2026-08-19 16:24:51.476468
915	redis	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
916	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
917	celery	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
918	email	HEALTHY	\N	2026-08-19 16:24:51.476468
919	backup	UNAVAILABLE	\N	2026-08-19 16:24:51.476468
920	sentry	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
921	openai	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
922	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:24:51.476468
923	simulation	HEALTHY	\N	2026-08-19 16:24:51.476468
924	application	HEALTHY	4.5	2026-08-19 16:24:51.476468
925	database	HEALTHY	0	2026-08-19 16:25:21.502303
926	redis	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
927	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
928	celery	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
929	email	HEALTHY	\N	2026-08-19 16:25:21.503337
930	backup	UNAVAILABLE	\N	2026-08-19 16:25:21.503337
931	sentry	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
932	openai	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
933	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:25:21.503337
934	simulation	HEALTHY	\N	2026-08-19 16:25:21.503337
935	application	HEALTHY	4.5	2026-08-19 16:25:21.503337
1244	database	HEALTHY	5	2026-08-19 16:39:52.867529
1245	redis	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1246	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1247	celery	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1248	email	HEALTHY	\N	2026-08-19 16:39:52.868526
1249	backup	UNAVAILABLE	\N	2026-08-19 16:39:52.868526
1250	sentry	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1251	openai	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1252	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:39:52.868526
1253	simulation	HEALTHY	\N	2026-08-19 16:39:52.868526
1254	application	HEALTHY	4.5	2026-08-19 16:39:52.868526
1365	database	HEALTHY	0	2026-08-19 16:45:23.700611
1366	redis	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1367	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1368	celery	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1369	email	HEALTHY	\N	2026-08-19 16:45:23.701999
1370	backup	UNAVAILABLE	\N	2026-08-19 16:45:23.701999
1371	sentry	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1372	openai	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1373	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:45:23.701999
1374	simulation	HEALTHY	\N	2026-08-19 16:45:23.701999
1375	application	HEALTHY	4.5	2026-08-19 16:45:23.70251
1420	database	HEALTHY	1	2026-08-19 16:47:53.920847
1421	redis	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1422	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1423	celery	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1424	email	HEALTHY	\N	2026-08-19 16:47:53.921847
1425	backup	UNAVAILABLE	\N	2026-08-19 16:47:53.921847
1426	sentry	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1427	openai	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1428	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:47:53.921847
1429	simulation	HEALTHY	\N	2026-08-19 16:47:53.921847
1430	application	HEALTHY	4.5	2026-08-19 16:47:53.921847
1519	database	HEALTHY	1.02	2026-08-19 16:52:24.329514
1520	redis	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1521	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1522	celery	NOT_CONFIGURED	\N	2026-08-19 16:52:24.329514
1523	email	HEALTHY	\N	2026-08-19 16:52:24.329514
1524	backup	UNAVAILABLE	\N	2026-08-19 16:52:24.330509
1525	sentry	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1526	openai	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1527	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:52:24.330509
1528	simulation	HEALTHY	\N	2026-08-19 16:52:24.330509
1529	application	HEALTHY	4.5	2026-08-19 16:52:24.330509
1618	database	HEALTHY	1	2026-08-19 16:56:54.646138
1619	redis	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1620	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1621	celery	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1622	email	HEALTHY	\N	2026-08-19 16:56:54.646138
1623	backup	UNAVAILABLE	\N	2026-08-19 16:56:54.646138
1624	sentry	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1625	openai	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1626	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:56:54.646138
1627	simulation	HEALTHY	\N	2026-08-19 16:56:54.646138
1628	application	HEALTHY	4.5	2026-08-19 16:56:54.646138
1640	database	HEALTHY	1	2026-08-19 16:57:54.722534
1641	redis	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1642	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1643	celery	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1644	email	HEALTHY	\N	2026-08-19 16:57:54.722534
1645	backup	UNAVAILABLE	\N	2026-08-19 16:57:54.722534
1646	sentry	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1647	openai	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1648	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:57:54.722534
1649	simulation	HEALTHY	\N	2026-08-19 16:57:54.722534
1650	application	HEALTHY	4.5	2026-08-19 16:57:54.722534
1728	database	HEALTHY	0	2026-08-19 17:01:55.137988
1729	redis	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1730	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1731	celery	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1732	email	HEALTHY	\N	2026-08-19 17:01:55.137988
1733	backup	UNAVAILABLE	\N	2026-08-19 17:01:55.137988
1734	sentry	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1735	openai	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1736	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:01:55.137988
1737	simulation	HEALTHY	\N	2026-08-19 17:01:55.137988
1738	application	HEALTHY	4.5	2026-08-19 17:01:55.137988
1882	database	HEALTHY	0.98	2026-08-19 17:08:55.627902
1883	redis	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1884	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1885	celery	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1886	email	HEALTHY	\N	2026-08-19 17:08:55.627902
1887	backup	UNAVAILABLE	\N	2026-08-19 17:08:55.627902
1888	sentry	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1889	openai	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1890	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:08:55.627902
1891	simulation	HEALTHY	\N	2026-08-19 17:08:55.627902
1892	application	HEALTHY	4.5	2026-08-19 17:08:55.627902
1920	backup	UNAVAILABLE	\N	2026-08-19 17:10:25.715988
1921	sentry	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1922	openai	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1923	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1924	simulation	HEALTHY	\N	2026-08-19 17:10:25.715988
1925	application	HEALTHY	4.5	2026-08-19 17:10:25.715988
1937	database	HEALTHY	1	2026-08-19 17:11:25.815368
1938	redis	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1939	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1940	celery	NOT_CONFIGURED	\N	2026-08-19 17:11:25.815368
1941	email	HEALTHY	\N	2026-08-19 17:11:25.816366
1942	backup	UNAVAILABLE	\N	2026-08-19 17:11:25.816366
1943	sentry	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1944	openai	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1945	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:11:25.816366
1946	simulation	HEALTHY	\N	2026-08-19 17:11:25.816366
1947	application	HEALTHY	4.5	2026-08-19 17:11:25.816366
1959	database	HEALTHY	0	2026-08-19 17:12:25.894247
1960	redis	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1961	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1962	celery	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1963	email	HEALTHY	\N	2026-08-19 17:12:25.895254
1964	backup	UNAVAILABLE	\N	2026-08-19 17:12:25.895254
1965	sentry	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1966	openai	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1967	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:12:25.895254
1968	simulation	HEALTHY	\N	2026-08-19 17:12:25.895254
1969	application	HEALTHY	4.5	2026-08-19 17:12:25.895254
1979	simulation	HEALTHY	\N	2026-08-19 17:12:55.919062
1980	application	HEALTHY	4.5	2026-08-19 17:12:55.919062
1981	database	HEALTHY	1	2026-08-19 17:13:25.942114
1982	redis	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
1983	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
1984	celery	NOT_CONFIGURED	\N	2026-08-19 17:13:25.942114
936	database	HEALTHY	1.02	2026-08-19 16:25:51.532387
937	redis	NOT_CONFIGURED	\N	2026-08-19 16:25:51.532387
938	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:25:51.532387
939	celery	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
940	email	HEALTHY	\N	2026-08-19 16:25:51.53339
941	backup	UNAVAILABLE	\N	2026-08-19 16:25:51.53339
942	sentry	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
943	openai	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
944	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:25:51.53339
945	simulation	HEALTHY	\N	2026-08-19 16:25:51.53339
946	application	HEALTHY	4.5	2026-08-19 16:25:51.53339
947	database	HEALTHY	1.2	2026-08-19 16:26:21.566467
948	redis	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
949	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
950	celery	NOT_CONFIGURED	\N	2026-08-19 16:26:21.566467
951	email	HEALTHY	\N	2026-08-19 16:26:21.566467
952	backup	UNAVAILABLE	\N	2026-08-19 16:26:21.566467
953	sentry	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
954	openai	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
955	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:26:21.567666
956	simulation	HEALTHY	\N	2026-08-19 16:26:21.567666
957	application	HEALTHY	4.5	2026-08-19 16:26:21.567666
958	database	HEALTHY	0	2026-08-19 16:26:51.709669
959	redis	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
960	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
961	celery	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
962	email	HEALTHY	\N	2026-08-19 16:26:51.709669
963	backup	UNAVAILABLE	\N	2026-08-19 16:26:51.709669
964	sentry	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
965	openai	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
966	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:26:51.709669
967	simulation	HEALTHY	\N	2026-08-19 16:26:51.709669
968	application	HEALTHY	4.5	2026-08-19 16:26:51.709669
969	database	HEALTHY	0	2026-08-19 16:27:21.740383
970	redis	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
971	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
972	celery	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
973	email	HEALTHY	\N	2026-08-19 16:27:21.740383
974	backup	UNAVAILABLE	\N	2026-08-19 16:27:21.740383
975	sentry	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
976	openai	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
977	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:27:21.740383
978	simulation	HEALTHY	\N	2026-08-19 16:27:21.740383
979	application	HEALTHY	4.5	2026-08-19 16:27:21.740383
980	database	HEALTHY	2.99	2026-08-19 16:27:51.799375
981	redis	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
982	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
983	celery	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
984	email	HEALTHY	\N	2026-08-19 16:27:51.799375
985	backup	UNAVAILABLE	\N	2026-08-19 16:27:51.799375
986	sentry	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
987	openai	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
988	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:27:51.799375
989	simulation	HEALTHY	\N	2026-08-19 16:27:51.799375
990	application	HEALTHY	4.5	2026-08-19 16:27:51.799375
991	database	HEALTHY	1	2026-08-19 16:28:21.849607
992	redis	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
993	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
994	celery	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
995	email	HEALTHY	\N	2026-08-19 16:28:21.849607
996	backup	UNAVAILABLE	\N	2026-08-19 16:28:21.849607
997	sentry	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
998	openai	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
999	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:28:21.849607
1000	simulation	HEALTHY	\N	2026-08-19 16:28:21.849607
1001	application	HEALTHY	4.5	2026-08-19 16:28:21.849607
1002	database	HEALTHY	1.01	2026-08-19 16:28:51.88422
1003	redis	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1004	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1005	celery	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1006	email	HEALTHY	\N	2026-08-19 16:28:51.88422
1007	backup	UNAVAILABLE	\N	2026-08-19 16:28:51.88422
1008	sentry	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1009	openai	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1010	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:28:51.88422
1011	simulation	HEALTHY	\N	2026-08-19 16:28:51.88422
1012	application	HEALTHY	4.5	2026-08-19 16:28:51.88422
1013	database	HEALTHY	0	2026-08-19 16:29:21.917869
1014	redis	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1015	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1016	celery	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1017	email	HEALTHY	\N	2026-08-19 16:29:21.917869
1018	backup	UNAVAILABLE	\N	2026-08-19 16:29:21.917869
1019	sentry	NOT_CONFIGURED	\N	2026-08-19 16:29:21.917869
1020	openai	NOT_CONFIGURED	\N	2026-08-19 16:29:21.918885
1021	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:29:21.918885
1022	simulation	HEALTHY	\N	2026-08-19 16:29:21.918885
1023	application	HEALTHY	4.5	2026-08-19 16:29:21.918885
1024	database	HEALTHY	0	2026-08-19 16:29:51.951829
1025	redis	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1026	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1027	celery	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1028	email	HEALTHY	\N	2026-08-19 16:29:51.951829
1029	backup	UNAVAILABLE	\N	2026-08-19 16:29:51.951829
1030	sentry	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1031	openai	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1032	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:29:51.951829
1033	simulation	HEALTHY	\N	2026-08-19 16:29:51.951829
1034	application	HEALTHY	4.5	2026-08-19 16:29:51.951829
1035	database	HEALTHY	0	2026-08-19 16:30:21.983472
1036	redis	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1037	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1038	celery	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1039	email	HEALTHY	\N	2026-08-19 16:30:21.983472
1040	backup	UNAVAILABLE	\N	2026-08-19 16:30:21.983472
1041	sentry	NOT_CONFIGURED	\N	2026-08-19 16:30:21.983472
1042	openai	NOT_CONFIGURED	\N	2026-08-19 16:30:21.98526
1043	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:30:21.98526
1044	simulation	HEALTHY	\N	2026-08-19 16:30:21.98526
1045	application	HEALTHY	4.5	2026-08-19 16:30:21.98526
1046	database	HEALTHY	0	2026-08-19 16:30:52.00886
1047	redis	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1048	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1049	celery	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1050	email	HEALTHY	\N	2026-08-19 16:30:52.00886
1051	backup	UNAVAILABLE	\N	2026-08-19 16:30:52.00886
1052	sentry	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1053	openai	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1054	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:30:52.00886
1055	simulation	HEALTHY	\N	2026-08-19 16:30:52.00886
1056	application	HEALTHY	4.5	2026-08-19 16:30:52.00886
1057	database	HEALTHY	4	2026-08-19 16:31:22.11501
1058	redis	NOT_CONFIGURED	\N	2026-08-19 16:31:22.11501
1059	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1060	celery	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1061	email	HEALTHY	\N	2026-08-19 16:31:22.116014
1062	backup	UNAVAILABLE	\N	2026-08-19 16:31:22.116014
1063	sentry	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1064	openai	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1065	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:31:22.116014
1066	simulation	HEALTHY	\N	2026-08-19 16:31:22.116014
1067	application	HEALTHY	4.5	2026-08-19 16:31:22.116014
1255	database	HEALTHY	1	2026-08-19 16:40:22.915684
1256	redis	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1257	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1258	celery	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1259	email	HEALTHY	\N	2026-08-19 16:40:22.916712
1260	backup	UNAVAILABLE	\N	2026-08-19 16:40:22.916712
1261	sentry	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1262	openai	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1263	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:40:22.916712
1264	simulation	HEALTHY	\N	2026-08-19 16:40:22.916712
1265	application	HEALTHY	4.5	2026-08-19 16:40:22.916712
1266	database	HEALTHY	1.02	2026-08-19 16:40:52.952825
1267	redis	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1268	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1269	celery	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1270	email	HEALTHY	\N	2026-08-19 16:40:52.952825
1271	backup	UNAVAILABLE	\N	2026-08-19 16:40:52.952825
1272	sentry	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1273	openai	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1274	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:40:52.952825
1275	simulation	HEALTHY	\N	2026-08-19 16:40:52.952825
1276	application	HEALTHY	4.5	2026-08-19 16:40:52.953826
1398	database	HEALTHY	1	2026-08-19 16:46:53.826913
1399	redis	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1400	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1401	celery	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1402	email	HEALTHY	\N	2026-08-19 16:46:53.826913
1403	backup	UNAVAILABLE	\N	2026-08-19 16:46:53.826913
1404	sentry	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1405	openai	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1406	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:46:53.826913
1407	simulation	HEALTHY	\N	2026-08-19 16:46:53.826913
1408	application	HEALTHY	4.5	2026-08-19 16:46:53.826913
1431	database	HEALTHY	0	2026-08-19 16:48:23.956056
1432	redis	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1433	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1434	celery	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1435	email	HEALTHY	\N	2026-08-19 16:48:23.956056
1436	backup	UNAVAILABLE	\N	2026-08-19 16:48:23.956056
1437	sentry	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1438	openai	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1439	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:48:23.956056
1440	simulation	HEALTHY	\N	2026-08-19 16:48:23.956056
1441	application	HEALTHY	4.5	2026-08-19 16:48:23.956056
1530	database	HEALTHY	1	2026-08-19 16:52:54.367201
1531	redis	NOT_CONFIGURED	\N	2026-08-19 16:52:54.367201
1532	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1533	celery	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1534	email	HEALTHY	\N	2026-08-19 16:52:54.368216
1535	backup	UNAVAILABLE	\N	2026-08-19 16:52:54.368216
1536	sentry	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1537	openai	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1538	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:52:54.368216
1539	simulation	HEALTHY	\N	2026-08-19 16:52:54.368216
1540	application	HEALTHY	4.5	2026-08-19 16:52:54.368216
1596	database	HEALTHY	1	2026-08-19 16:55:54.58314
1597	redis	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1598	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1599	celery	NOT_CONFIGURED	\N	2026-08-19 16:55:54.584144
1600	email	HEALTHY	\N	2026-08-19 16:55:54.585141
1601	backup	UNAVAILABLE	\N	2026-08-19 16:55:54.585141
1602	sentry	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1603	openai	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1604	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:55:54.585141
1605	simulation	HEALTHY	\N	2026-08-19 16:55:54.585141
1606	application	HEALTHY	4.5	2026-08-19 16:55:54.585141
1673	database	HEALTHY	0	2026-08-19 16:59:24.861661
1674	redis	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1675	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1676	celery	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1677	email	HEALTHY	\N	2026-08-19 16:59:24.861661
1678	backup	UNAVAILABLE	\N	2026-08-19 16:59:24.861661
1679	sentry	NOT_CONFIGURED	\N	2026-08-19 16:59:24.861661
1680	openai	NOT_CONFIGURED	\N	2026-08-19 16:59:24.862679
1681	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:59:24.862679
1682	simulation	HEALTHY	\N	2026-08-19 16:59:24.862679
1683	application	HEALTHY	4.5	2026-08-19 16:59:24.862679
1750	database	HEALTHY	0	2026-08-19 17:02:55.210583
1751	redis	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1752	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1753	celery	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1754	email	HEALTHY	\N	2026-08-19 17:02:55.210583
1755	backup	UNAVAILABLE	\N	2026-08-19 17:02:55.210583
1756	sentry	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1757	openai	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1758	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:02:55.210583
1759	simulation	HEALTHY	\N	2026-08-19 17:02:55.210583
1760	application	HEALTHY	4.5	2026-08-19 17:02:55.210583
1772	database	HEALTHY	1	2026-08-19 17:03:55.272424
1773	redis	NOT_CONFIGURED	\N	2026-08-19 17:03:55.272424
1774	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1775	celery	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1776	email	HEALTHY	\N	2026-08-19 17:03:55.273424
1777	backup	UNAVAILABLE	\N	2026-08-19 17:03:55.273424
1778	sentry	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1779	openai	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1780	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:03:55.273424
1781	simulation	HEALTHY	\N	2026-08-19 17:03:55.273424
1782	application	HEALTHY	4.5	2026-08-19 17:03:55.273424
1893	database	HEALTHY	0.99	2026-08-19 17:09:25.651834
1894	redis	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1895	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1896	celery	NOT_CONFIGURED	\N	2026-08-19 17:09:25.651834
1897	email	HEALTHY	\N	2026-08-19 17:09:25.652832
1898	backup	UNAVAILABLE	\N	2026-08-19 17:09:25.652832
1899	sentry	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1900	openai	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1901	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:09:25.652832
1902	simulation	HEALTHY	\N	2026-08-19 17:09:25.652832
1903	application	HEALTHY	4.5	2026-08-19 17:09:25.652832
1926	database	HEALTHY	0	2026-08-19 17:10:55.749965
1927	redis	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1928	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1929	celery	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1930	email	HEALTHY	\N	2026-08-19 17:10:55.749965
1931	backup	UNAVAILABLE	\N	2026-08-19 17:10:55.749965
1068	database	HEALTHY	0	2026-08-19 16:31:52.153956
1069	redis	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1070	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1071	celery	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1072	email	HEALTHY	\N	2026-08-19 16:31:52.154953
1073	backup	UNAVAILABLE	\N	2026-08-19 16:31:52.154953
1074	sentry	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1075	openai	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1076	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:31:52.154953
1077	simulation	HEALTHY	\N	2026-08-19 16:31:52.154953
1078	application	HEALTHY	4.5	2026-08-19 16:31:52.154953
1277	database	HEALTHY	0.99	2026-08-19 16:41:22.98843
1278	redis	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1279	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1280	celery	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1281	email	HEALTHY	\N	2026-08-19 16:41:22.98843
1282	backup	UNAVAILABLE	\N	2026-08-19 16:41:22.98843
1283	sentry	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1284	openai	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1285	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:41:22.98843
1286	simulation	HEALTHY	\N	2026-08-19 16:41:22.989435
1287	application	HEALTHY	4.5	2026-08-19 16:41:22.989435
1442	database	HEALTHY	0	2026-08-19 16:48:53.990295
1443	redis	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1444	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1445	celery	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1446	email	HEALTHY	\N	2026-08-19 16:48:53.990295
1447	backup	UNAVAILABLE	\N	2026-08-19 16:48:53.990295
1448	sentry	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1449	openai	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1450	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:48:53.990295
1451	simulation	HEALTHY	\N	2026-08-19 16:48:53.990295
1452	application	HEALTHY	4.5	2026-08-19 16:48:53.990295
1552	database	HEALTHY	1	2026-08-19 16:53:54.446557
1553	redis	NOT_CONFIGURED	\N	2026-08-19 16:53:54.446557
1554	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:53:54.446557
1555	celery	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1556	email	HEALTHY	\N	2026-08-19 16:53:54.447557
1557	backup	UNAVAILABLE	\N	2026-08-19 16:53:54.447557
1558	sentry	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1559	openai	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1560	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:53:54.447557
1561	simulation	HEALTHY	\N	2026-08-19 16:53:54.447557
1562	application	HEALTHY	4.5	2026-08-19 16:53:54.447557
1629	database	HEALTHY	1	2026-08-19 16:57:24.676924
1630	redis	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1631	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1632	celery	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1633	email	HEALTHY	\N	2026-08-19 16:57:24.676924
1634	backup	UNAVAILABLE	\N	2026-08-19 16:57:24.676924
1635	sentry	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1636	openai	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1637	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:57:24.676924
1638	simulation	HEALTHY	\N	2026-08-19 16:57:24.676924
1639	application	HEALTHY	4.5	2026-08-19 16:57:24.676924
1684	database	HEALTHY	0	2026-08-19 16:59:54.900707
1685	redis	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1686	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1687	celery	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1688	email	HEALTHY	\N	2026-08-19 16:59:54.900707
1689	backup	UNAVAILABLE	\N	2026-08-19 16:59:54.900707
1690	sentry	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1691	openai	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1692	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:59:54.900707
1693	simulation	HEALTHY	\N	2026-08-19 16:59:54.900707
1694	application	HEALTHY	4.5	2026-08-19 16:59:54.901707
1805	database	HEALTHY	0	2026-08-19 17:05:25.393812
1806	redis	NOT_CONFIGURED	\N	2026-08-19 17:05:25.393812
1807	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1808	celery	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1809	email	HEALTHY	\N	2026-08-19 17:05:25.395155
1810	backup	UNAVAILABLE	\N	2026-08-19 17:05:25.395155
1811	sentry	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1812	openai	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1813	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:05:25.395155
1814	simulation	HEALTHY	\N	2026-08-19 17:05:25.395155
1815	application	HEALTHY	4.5	2026-08-19 17:05:25.395155
1871	database	HEALTHY	1	2026-08-19 17:08:25.599105
1872	redis	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1873	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1874	celery	NOT_CONFIGURED	\N	2026-08-19 17:08:25.599105
1875	email	HEALTHY	\N	2026-08-19 17:08:25.600226
1876	backup	UNAVAILABLE	\N	2026-08-19 17:08:25.600226
1877	sentry	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1878	openai	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1879	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:08:25.600226
1880	simulation	HEALTHY	\N	2026-08-19 17:08:25.600226
1881	application	HEALTHY	4.5	2026-08-19 17:08:25.600226
1904	database	HEALTHY	0	2026-08-19 17:09:55.684407
1905	redis	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1906	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1907	celery	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1908	email	HEALTHY	\N	2026-08-19 17:09:55.684407
1909	backup	UNAVAILABLE	\N	2026-08-19 17:09:55.684407
1910	sentry	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1911	openai	NOT_CONFIGURED	\N	2026-08-19 17:09:55.684407
1912	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:09:55.685409
1913	simulation	HEALTHY	\N	2026-08-19 17:09:55.685409
1914	application	HEALTHY	4.5	2026-08-19 17:09:55.685409
1932	sentry	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1933	openai	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1934	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:10:55.749965
1935	simulation	HEALTHY	\N	2026-08-19 17:10:55.749965
1936	application	HEALTHY	4.5	2026-08-19 17:10:55.749965
1948	database	HEALTHY	0	2026-08-19 17:11:55.854241
1949	redis	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1950	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1951	celery	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1952	email	HEALTHY	\N	2026-08-19 17:11:55.854241
1953	backup	UNAVAILABLE	\N	2026-08-19 17:11:55.854241
1954	sentry	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1955	openai	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1956	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:11:55.854241
1957	simulation	HEALTHY	\N	2026-08-19 17:11:55.854241
1958	application	HEALTHY	4.5	2026-08-19 17:11:55.854241
1970	database	HEALTHY	1.03	2026-08-19 17:12:55.91806
1971	redis	NOT_CONFIGURED	\N	2026-08-19 17:12:55.91806
1972	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:12:55.91806
1973	celery	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1974	email	HEALTHY	\N	2026-08-19 17:12:55.919062
1975	backup	UNAVAILABLE	\N	2026-08-19 17:12:55.919062
1976	sentry	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1977	openai	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1978	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:12:55.919062
1079	database	HEALTHY	1.04	2026-08-19 16:32:22.185859
1080	redis	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1081	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1082	celery	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1083	email	HEALTHY	\N	2026-08-19 16:32:22.186818
1084	backup	UNAVAILABLE	\N	2026-08-19 16:32:22.186818
1085	sentry	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1086	openai	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1087	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:32:22.186818
1088	simulation	HEALTHY	\N	2026-08-19 16:32:22.186818
1089	application	HEALTHY	4.5	2026-08-19 16:32:22.186818
1288	database	HEALTHY	0	2026-08-19 16:41:53.039874
1289	redis	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1290	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1291	celery	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1292	email	HEALTHY	\N	2026-08-19 16:41:53.039874
1293	backup	UNAVAILABLE	\N	2026-08-19 16:41:53.039874
1294	sentry	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1295	openai	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1296	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:41:53.039874
1297	simulation	HEALTHY	\N	2026-08-19 16:41:53.039874
1298	application	HEALTHY	4.5	2026-08-19 16:41:53.039874
1310	database	HEALTHY	1	2026-08-19 16:42:53.12398
1311	redis	NOT_CONFIGURED	\N	2026-08-19 16:42:53.12398
1312	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:42:53.12398
1313	celery	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1314	email	HEALTHY	\N	2026-08-19 16:42:53.125099
1315	backup	UNAVAILABLE	\N	2026-08-19 16:42:53.125099
1316	sentry	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1317	openai	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1318	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:42:53.125099
1319	simulation	HEALTHY	\N	2026-08-19 16:42:53.125099
1320	application	HEALTHY	4.5	2026-08-19 16:42:53.125099
1332	database	HEALTHY	1.02	2026-08-19 16:43:53.236274
1333	redis	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1334	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1335	celery	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1336	email	HEALTHY	\N	2026-08-19 16:43:53.236274
1337	backup	UNAVAILABLE	\N	2026-08-19 16:43:53.236274
1338	sentry	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1339	openai	NOT_CONFIGURED	\N	2026-08-19 16:43:53.236274
1340	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:43:53.237251
1341	simulation	HEALTHY	\N	2026-08-19 16:43:53.237251
1342	application	HEALTHY	4.5	2026-08-19 16:43:53.237251
1475	database	HEALTHY	1.17	2026-08-19 16:50:24.100571
1476	redis	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1477	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1478	celery	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1479	email	HEALTHY	\N	2026-08-19 16:50:24.100571
1480	backup	UNAVAILABLE	\N	2026-08-19 16:50:24.100571
1481	sentry	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1482	openai	NOT_CONFIGURED	\N	2026-08-19 16:50:24.100571
1483	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:50:24.101579
1484	simulation	HEALTHY	\N	2026-08-19 16:50:24.101579
1485	application	HEALTHY	4.5	2026-08-19 16:50:24.101579
1541	database	HEALTHY	0.96	2026-08-19 16:53:24.409707
1542	redis	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1543	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1544	celery	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1545	email	HEALTHY	\N	2026-08-19 16:53:24.409707
1546	backup	UNAVAILABLE	\N	2026-08-19 16:53:24.409707
1547	sentry	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1548	openai	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1549	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:53:24.409707
1550	simulation	HEALTHY	\N	2026-08-19 16:53:24.409707
1551	application	HEALTHY	4.5	2026-08-19 16:53:24.409707
1563	database	HEALTHY	1	2026-08-19 16:54:24.482785
1564	redis	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1565	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1566	celery	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1567	email	HEALTHY	\N	2026-08-19 16:54:24.483784
1568	backup	UNAVAILABLE	\N	2026-08-19 16:54:24.483784
1569	sentry	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1570	openai	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1571	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:54:24.483784
1572	simulation	HEALTHY	\N	2026-08-19 16:54:24.483784
1573	application	HEALTHY	4.5	2026-08-19 16:54:24.483784
1651	database	HEALTHY	0	2026-08-19 16:58:24.777371
1652	redis	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1653	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1654	celery	NOT_CONFIGURED	\N	2026-08-19 16:58:24.777371
1655	email	HEALTHY	\N	2026-08-19 16:58:24.777371
1656	backup	UNAVAILABLE	\N	2026-08-19 16:58:24.778378
1657	sentry	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1658	openai	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1659	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:58:24.778378
1660	simulation	HEALTHY	\N	2026-08-19 16:58:24.778378
1661	application	HEALTHY	4.5	2026-08-19 16:58:24.778378
1695	database	HEALTHY	1	2026-08-19 17:00:24.962356
1696	redis	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1697	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1698	celery	NOT_CONFIGURED	\N	2026-08-19 17:00:24.962356
1699	email	HEALTHY	\N	2026-08-19 17:00:24.962356
1700	backup	UNAVAILABLE	\N	2026-08-19 17:00:24.962356
1701	sentry	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1702	openai	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1703	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:00:24.963357
1704	simulation	HEALTHY	\N	2026-08-19 17:00:24.963357
1705	application	HEALTHY	4.5	2026-08-19 17:00:24.963357
1739	database	HEALTHY	0	2026-08-19 17:02:25.177388
1740	redis	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1741	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1742	celery	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1743	email	HEALTHY	\N	2026-08-19 17:02:25.177388
1744	backup	UNAVAILABLE	\N	2026-08-19 17:02:25.177388
1745	sentry	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1746	openai	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1747	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:02:25.177388
1748	simulation	HEALTHY	\N	2026-08-19 17:02:25.177388
1749	application	HEALTHY	4.5	2026-08-19 17:02:25.177388
1816	database	HEALTHY	0.97	2026-08-19 17:05:55.431079
1817	redis	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1818	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1819	celery	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1820	email	HEALTHY	\N	2026-08-19 17:05:55.431079
1821	backup	UNAVAILABLE	\N	2026-08-19 17:05:55.431079
1822	sentry	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1823	openai	NOT_CONFIGURED	\N	2026-08-19 17:05:55.431079
1824	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:05:55.432081
1825	simulation	HEALTHY	\N	2026-08-19 17:05:55.432081
1826	application	HEALTHY	4.5	2026-08-19 17:05:55.432081
1827	database	HEALTHY	1	2026-08-19 17:06:25.467058
1828	redis	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1829	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1090	database	HEALTHY	0	2026-08-19 16:32:52.218544
1091	redis	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1092	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1093	celery	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1094	email	HEALTHY	\N	2026-08-19 16:32:52.218544
1095	backup	UNAVAILABLE	\N	2026-08-19 16:32:52.218544
1096	sentry	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1097	openai	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1098	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:32:52.218544
1099	simulation	HEALTHY	\N	2026-08-19 16:32:52.218544
1100	application	HEALTHY	4.5	2026-08-19 16:32:52.218544
1101	database	HEALTHY	0.99	2026-08-19 16:33:22.244293
1102	redis	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1103	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1104	celery	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1105	email	HEALTHY	\N	2026-08-19 16:33:22.245293
1106	backup	UNAVAILABLE	\N	2026-08-19 16:33:22.245293
1107	sentry	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1108	openai	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1109	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:33:22.245293
1110	simulation	HEALTHY	\N	2026-08-19 16:33:22.245293
1111	application	HEALTHY	4.5	2026-08-19 16:33:22.245293
1112	database	HEALTHY	3.11	2026-08-19 16:33:52.306064
1113	redis	NOT_CONFIGURED	\N	2026-08-19 16:33:52.306064
1114	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:33:52.306064
1115	celery	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1116	email	HEALTHY	\N	2026-08-19 16:33:52.307043
1117	backup	UNAVAILABLE	\N	2026-08-19 16:33:52.307043
1118	sentry	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1119	openai	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1120	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:33:52.307043
1121	simulation	HEALTHY	\N	2026-08-19 16:33:52.307043
1122	application	HEALTHY	4.5	2026-08-19 16:33:52.307043
1123	database	HEALTHY	0	2026-08-19 16:34:22.357495
1124	redis	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1125	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1126	celery	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1127	email	HEALTHY	\N	2026-08-19 16:34:22.357495
1128	backup	UNAVAILABLE	\N	2026-08-19 16:34:22.357495
1129	sentry	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1130	openai	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1131	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:34:22.357495
1132	simulation	HEALTHY	\N	2026-08-19 16:34:22.357495
1133	application	HEALTHY	4.5	2026-08-19 16:34:22.358492
1134	database	HEALTHY	1	2026-08-19 16:34:52.402575
1135	redis	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1136	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1137	celery	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1138	email	HEALTHY	\N	2026-08-19 16:34:52.403576
1139	backup	UNAVAILABLE	\N	2026-08-19 16:34:52.403576
1140	sentry	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1141	openai	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1142	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:34:52.403576
1143	simulation	HEALTHY	\N	2026-08-19 16:34:52.403576
1144	application	HEALTHY	4.5	2026-08-19 16:34:52.403576
1145	database	HEALTHY	0.97	2026-08-19 16:35:22.443843
1146	redis	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1147	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1148	celery	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1149	email	HEALTHY	\N	2026-08-19 16:35:22.443843
1150	backup	UNAVAILABLE	\N	2026-08-19 16:35:22.443843
1151	sentry	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1152	openai	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1153	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:35:22.443843
1154	simulation	HEALTHY	\N	2026-08-19 16:35:22.443843
1155	application	HEALTHY	4.5	2026-08-19 16:35:22.443843
1156	database	HEALTHY	0	2026-08-19 16:35:52.503398
1157	redis	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1158	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1159	celery	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1160	email	HEALTHY	\N	2026-08-19 16:35:52.503398
1161	backup	UNAVAILABLE	\N	2026-08-19 16:35:52.503398
1162	sentry	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1163	openai	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1164	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:35:52.503398
1165	simulation	HEALTHY	\N	2026-08-19 16:35:52.503398
1166	application	HEALTHY	4.5	2026-08-19 16:35:52.503398
1167	database	HEALTHY	1	2026-08-19 16:36:22.539664
1168	redis	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1169	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1170	celery	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1171	email	HEALTHY	\N	2026-08-19 16:36:22.539664
1172	backup	UNAVAILABLE	\N	2026-08-19 16:36:22.539664
1173	sentry	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1174	openai	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1175	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:36:22.539664
1176	simulation	HEALTHY	\N	2026-08-19 16:36:22.539664
1177	application	HEALTHY	4.5	2026-08-19 16:36:22.54062
1178	database	HEALTHY	0.97	2026-08-19 16:36:52.574143
1179	redis	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1180	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1181	celery	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1182	email	HEALTHY	\N	2026-08-19 16:36:52.574143
1183	backup	UNAVAILABLE	\N	2026-08-19 16:36:52.574143
1184	sentry	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1185	openai	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1186	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:36:52.574143
1187	simulation	HEALTHY	\N	2026-08-19 16:36:52.574143
1188	application	HEALTHY	4.5	2026-08-19 16:36:52.574143
1189	database	HEALTHY	0.99	2026-08-19 16:37:22.610649
1190	redis	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1191	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1192	celery	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1193	email	HEALTHY	\N	2026-08-19 16:37:22.610649
1194	backup	UNAVAILABLE	\N	2026-08-19 16:37:22.610649
1195	sentry	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1196	openai	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1197	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:37:22.610649
1198	simulation	HEALTHY	\N	2026-08-19 16:37:22.612
1199	application	HEALTHY	4.5	2026-08-19 16:37:22.612
1200	database	HEALTHY	0	2026-08-19 16:37:52.647498
1201	redis	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1202	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1203	celery	NOT_CONFIGURED	\N	2026-08-19 16:37:52.647498
1204	email	HEALTHY	\N	2026-08-19 16:37:52.647498
1205	backup	UNAVAILABLE	\N	2026-08-19 16:37:52.648498
1206	sentry	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1207	openai	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1208	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:37:52.648498
1209	simulation	HEALTHY	\N	2026-08-19 16:37:52.648498
1210	application	HEALTHY	4.5	2026-08-19 16:37:52.648498
1211	database	HEALTHY	1.01	2026-08-19 16:38:22.697947
1212	redis	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1213	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1214	celery	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1215	email	HEALTHY	\N	2026-08-19 16:38:22.698948
1216	backup	UNAVAILABLE	\N	2026-08-19 16:38:22.698948
1217	sentry	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1218	openai	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1219	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:38:22.698948
1220	simulation	HEALTHY	\N	2026-08-19 16:38:22.698948
1221	application	HEALTHY	4.5	2026-08-19 16:38:22.698948
1299	database	HEALTHY	1.01	2026-08-19 16:42:23.083042
1300	redis	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1301	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1302	celery	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1303	email	HEALTHY	\N	2026-08-19 16:42:23.083042
1304	backup	UNAVAILABLE	\N	2026-08-19 16:42:23.083042
1305	sentry	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1306	openai	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1307	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:42:23.083042
1308	simulation	HEALTHY	\N	2026-08-19 16:42:23.083042
1309	application	HEALTHY	4.5	2026-08-19 16:42:23.083042
1321	database	HEALTHY	3	2026-08-19 16:43:23.200799
1322	redis	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1323	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1324	celery	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1325	email	HEALTHY	\N	2026-08-19 16:43:23.200799
1326	backup	UNAVAILABLE	\N	2026-08-19 16:43:23.200799
1327	sentry	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1328	openai	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1329	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:43:23.200799
1330	simulation	HEALTHY	\N	2026-08-19 16:43:23.200799
1331	application	HEALTHY	4.5	2026-08-19 16:43:23.200799
1376	database	HEALTHY	0	2026-08-19 16:45:53.744071
1377	redis	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1378	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1379	celery	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1380	email	HEALTHY	\N	2026-08-19 16:45:53.744071
1381	backup	UNAVAILABLE	\N	2026-08-19 16:45:53.744071
1382	sentry	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1383	openai	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1384	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:45:53.744071
1385	simulation	HEALTHY	\N	2026-08-19 16:45:53.744071
1386	application	HEALTHY	4.5	2026-08-19 16:45:53.7451
1387	database	HEALTHY	1.09	2026-08-19 16:46:23.771516
1388	redis	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1389	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1390	celery	NOT_CONFIGURED	\N	2026-08-19 16:46:23.771516
1391	email	HEALTHY	\N	2026-08-19 16:46:23.771516
1392	backup	UNAVAILABLE	\N	2026-08-19 16:46:23.772522
1393	sentry	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1394	openai	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1395	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:46:23.772522
1396	simulation	HEALTHY	\N	2026-08-19 16:46:23.772522
1397	application	HEALTHY	4.5	2026-08-19 16:46:23.772522
1464	database	HEALTHY	0	2026-08-19 16:49:54.067979
1465	redis	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1466	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1467	celery	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1468	email	HEALTHY	\N	2026-08-19 16:49:54.067979
1469	backup	UNAVAILABLE	\N	2026-08-19 16:49:54.067979
1470	sentry	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1471	openai	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1472	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:49:54.067979
1473	simulation	HEALTHY	\N	2026-08-19 16:49:54.067979
1474	application	HEALTHY	4.5	2026-08-19 16:49:54.067979
1486	database	HEALTHY	0	2026-08-19 16:50:54.138581
1487	redis	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1488	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1489	celery	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1490	email	HEALTHY	\N	2026-08-19 16:50:54.139722
1491	backup	UNAVAILABLE	\N	2026-08-19 16:50:54.139722
1492	sentry	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1493	openai	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1494	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:50:54.139722
1495	simulation	HEALTHY	\N	2026-08-19 16:50:54.139722
1496	application	HEALTHY	4.5	2026-08-19 16:50:54.139722
1578	email	HEALTHY	\N	2026-08-19 16:54:54.524623
1579	backup	UNAVAILABLE	\N	2026-08-19 16:54:54.524623
1580	sentry	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1581	openai	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1582	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:54:54.524623
1583	simulation	HEALTHY	\N	2026-08-19 16:54:54.524623
1584	application	HEALTHY	4.5	2026-08-19 16:54:54.524623
1706	database	HEALTHY	1	2026-08-19 17:00:55.028197
1707	redis	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1708	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1709	celery	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1710	email	HEALTHY	\N	2026-08-19 17:00:55.028197
1711	backup	UNAVAILABLE	\N	2026-08-19 17:00:55.028197
1712	sentry	NOT_CONFIGURED	\N	2026-08-19 17:00:55.028197
1713	openai	NOT_CONFIGURED	\N	2026-08-19 17:00:55.029217
1714	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:00:55.029217
1715	simulation	HEALTHY	\N	2026-08-19 17:00:55.029217
1716	application	HEALTHY	4.5	2026-08-19 17:00:55.029217
1761	database	HEALTHY	0.61	2026-08-19 17:03:25.248021
1762	redis	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1763	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1764	celery	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1765	email	HEALTHY	\N	2026-08-19 17:03:25.248588
1766	backup	UNAVAILABLE	\N	2026-08-19 17:03:25.248588
1767	sentry	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1768	openai	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1769	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:03:25.248588
1770	simulation	HEALTHY	\N	2026-08-19 17:03:25.248588
1771	application	HEALTHY	4.5	2026-08-19 17:03:25.248588
1830	celery	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1831	email	HEALTHY	\N	2026-08-19 17:06:25.467058
1832	backup	UNAVAILABLE	\N	2026-08-19 17:06:25.467058
1833	sentry	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1834	openai	NOT_CONFIGURED	\N	2026-08-19 17:06:25.467058
1835	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:06:25.46803
1836	simulation	HEALTHY	\N	2026-08-19 17:06:25.46803
1837	application	HEALTHY	4.5	2026-08-19 17:06:25.46803
1838	database	HEALTHY	1	2026-08-19 17:06:55.509036
1839	redis	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1840	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1841	celery	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1842	email	HEALTHY	\N	2026-08-19 17:06:55.509036
1843	backup	UNAVAILABLE	\N	2026-08-19 17:06:55.509036
1844	sentry	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1845	openai	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1846	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:06:55.509036
1847	simulation	HEALTHY	\N	2026-08-19 17:06:55.509036
1848	application	HEALTHY	4.5	2026-08-19 17:06:55.509036
1915	database	HEALTHY	0	2026-08-19 17:10:25.715988
1916	redis	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1222	database	HEALTHY	1	2026-08-19 16:38:52.727668
1223	redis	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1224	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1225	celery	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1226	email	HEALTHY	\N	2026-08-19 16:38:52.728667
1227	backup	UNAVAILABLE	\N	2026-08-19 16:38:52.728667
1228	sentry	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1229	openai	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1230	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:38:52.728667
1231	simulation	HEALTHY	\N	2026-08-19 16:38:52.728667
1232	application	HEALTHY	4.5	2026-08-19 16:38:52.728667
1343	database	HEALTHY	4	2026-08-19 16:44:23.499576
1344	redis	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1345	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1346	celery	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1347	email	HEALTHY	\N	2026-08-19 16:44:23.499576
1348	backup	UNAVAILABLE	\N	2026-08-19 16:44:23.499576
1349	sentry	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1350	openai	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1351	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:44:23.499576
1352	simulation	HEALTHY	\N	2026-08-19 16:44:23.499576
1353	application	HEALTHY	4.5	2026-08-19 16:44:23.499576
1497	database	HEALTHY	0	2026-08-19 16:51:24.168832
1498	redis	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1499	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1500	celery	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1501	email	HEALTHY	\N	2026-08-19 16:51:24.168832
1502	backup	UNAVAILABLE	\N	2026-08-19 16:51:24.168832
1503	sentry	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1504	openai	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1505	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:51:24.168832
1506	simulation	HEALTHY	\N	2026-08-19 16:51:24.168832
1507	application	HEALTHY	4.5	2026-08-19 16:51:24.168832
1585	database	HEALTHY	0	2026-08-19 16:55:24.548226
1586	redis	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1587	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1588	celery	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1589	email	HEALTHY	\N	2026-08-19 16:55:24.548226
1590	backup	UNAVAILABLE	\N	2026-08-19 16:55:24.548226
1591	sentry	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1592	openai	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1593	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:55:24.548226
1594	simulation	HEALTHY	\N	2026-08-19 16:55:24.548226
1595	application	HEALTHY	4.5	2026-08-19 16:55:24.548226
1607	database	HEALTHY	1	2026-08-19 16:56:24.611586
1608	redis	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1609	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1610	celery	NOT_CONFIGURED	\N	2026-08-19 16:56:24.611586
1611	email	HEALTHY	\N	2026-08-19 16:56:24.612583
1612	backup	UNAVAILABLE	\N	2026-08-19 16:56:24.612583
1613	sentry	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1614	openai	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1615	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:56:24.612583
1616	simulation	HEALTHY	\N	2026-08-19 16:56:24.612583
1617	application	HEALTHY	4.5	2026-08-19 16:56:24.612583
1662	database	HEALTHY	0.99	2026-08-19 16:58:54.809106
1663	redis	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1664	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1665	celery	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1666	email	HEALTHY	\N	2026-08-19 16:58:54.809106
1667	backup	UNAVAILABLE	\N	2026-08-19 16:58:54.809106
1668	sentry	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1669	openai	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1670	cloudflare	NOT_CONFIGURED	\N	2026-08-19 16:58:54.809106
1671	simulation	HEALTHY	\N	2026-08-19 16:58:54.809106
1672	application	HEALTHY	4.5	2026-08-19 16:58:54.809106
1717	database	HEALTHY	0	2026-08-19 17:01:25.08102
1718	redis	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1719	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1720	celery	NOT_CONFIGURED	\N	2026-08-19 17:01:25.08102
1721	email	HEALTHY	\N	2026-08-19 17:01:25.082809
1722	backup	UNAVAILABLE	\N	2026-08-19 17:01:25.082809
1723	sentry	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1724	openai	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1725	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:01:25.082809
1726	simulation	HEALTHY	\N	2026-08-19 17:01:25.082809
1727	application	HEALTHY	4.5	2026-08-19 17:01:25.082809
1783	database	HEALTHY	0	2026-08-19 17:04:25.303586
1784	redis	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1785	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1786	celery	NOT_CONFIGURED	\N	2026-08-19 17:04:25.303586
1787	email	HEALTHY	\N	2026-08-19 17:04:25.304585
1788	backup	UNAVAILABLE	\N	2026-08-19 17:04:25.304585
1789	sentry	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1790	openai	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1791	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:04:25.304585
1792	simulation	HEALTHY	\N	2026-08-19 17:04:25.304585
1793	application	HEALTHY	4.5	2026-08-19 17:04:25.304585
1794	database	HEALTHY	2	2026-08-19 17:04:55.32883
1795	redis	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1796	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1797	celery	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32883
1798	email	HEALTHY	\N	2026-08-19 17:04:55.32983
1799	backup	UNAVAILABLE	\N	2026-08-19 17:04:55.32983
1800	sentry	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1801	openai	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1802	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:04:55.32983
1803	simulation	HEALTHY	\N	2026-08-19 17:04:55.32983
1804	application	HEALTHY	4.5	2026-08-19 17:04:55.32983
1849	database	HEALTHY	0	2026-08-19 17:07:25.558209
1850	redis	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1851	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1852	celery	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1853	email	HEALTHY	\N	2026-08-19 17:07:25.558209
1854	backup	UNAVAILABLE	\N	2026-08-19 17:07:25.558209
1855	sentry	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1856	openai	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1857	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:07:25.558209
1858	simulation	HEALTHY	\N	2026-08-19 17:07:25.558209
1859	application	HEALTHY	4.5	2026-08-19 17:07:25.558209
1860	database	HEALTHY	0	2026-08-19 17:07:55.577508
1861	redis	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1862	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1863	celery	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1864	email	HEALTHY	\N	2026-08-19 17:07:55.577508
1865	backup	UNAVAILABLE	\N	2026-08-19 17:07:55.577508
1866	sentry	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1867	openai	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1868	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:07:55.577508
1869	simulation	HEALTHY	\N	2026-08-19 17:07:55.577508
1870	application	HEALTHY	4.5	2026-08-19 17:07:55.577508
1917	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1918	celery	NOT_CONFIGURED	\N	2026-08-19 17:10:25.715988
1919	email	HEALTHY	\N	2026-08-19 17:10:25.715988
1985	email	HEALTHY	\N	2026-08-19 17:13:25.943111
1986	backup	UNAVAILABLE	\N	2026-08-19 17:13:25.943111
1987	sentry	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1988	openai	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1989	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:13:25.943111
1990	simulation	HEALTHY	\N	2026-08-19 17:13:25.943111
1991	application	HEALTHY	4.5	2026-08-19 17:13:25.943111
2047	database	HEALTHY	0	2026-08-19 17:16:26.257628
2048	redis	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2049	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2050	celery	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2051	email	HEALTHY	\N	2026-08-19 17:16:26.257628
2052	backup	UNAVAILABLE	\N	2026-08-19 17:16:26.257628
2053	sentry	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2054	openai	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2055	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:16:26.257628
2056	simulation	HEALTHY	\N	2026-08-19 17:16:26.257628
2057	application	HEALTHY	4.5	2026-08-19 17:16:26.257628
2795	database	HEALTHY	0	2026-08-19 18:15:44.241289
2796	redis	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2797	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2798	celery	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2799	email	HEALTHY	\N	2026-08-19 18:15:44.241289
2800	backup	UNAVAILABLE	\N	2026-08-19 18:15:44.241289
2801	sentry	NOT_CONFIGURED	\N	2026-08-19 18:15:44.241289
2802	openai	NOT_CONFIGURED	\N	2026-08-19 18:15:44.242286
2803	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:15:44.242286
2804	simulation	HEALTHY	\N	2026-08-19 18:15:44.242286
2805	application	HEALTHY	4.5	2026-08-19 18:15:44.242286
2861	database	HEALTHY	0	2026-08-19 18:18:44.638647
2862	redis	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2863	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2864	celery	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2865	email	HEALTHY	\N	2026-08-19 18:18:44.638647
2866	backup	UNAVAILABLE	\N	2026-08-19 18:18:44.638647
2867	sentry	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2868	openai	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2869	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:18:44.638647
2870	simulation	HEALTHY	\N	2026-08-19 18:18:44.638647
2871	application	HEALTHY	4.5	2026-08-19 18:18:44.638647
1992	database	HEALTHY	0.66	2026-08-19 17:13:55.979767
1993	redis	NOT_CONFIGURED	\N	2026-08-19 17:13:55.979767
1994	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:13:55.979767
1995	celery	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
1996	email	HEALTHY	\N	2026-08-19 17:13:55.980319
1997	backup	UNAVAILABLE	\N	2026-08-19 17:13:55.980319
1998	sentry	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
1999	openai	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
2000	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:13:55.980319
2001	simulation	HEALTHY	\N	2026-08-19 17:13:55.980319
2002	application	HEALTHY	4.5	2026-08-19 17:13:55.980319
2003	database	HEALTHY	0	2026-08-19 17:14:26.015046
2004	redis	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2005	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2006	celery	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2007	email	HEALTHY	\N	2026-08-19 17:14:26.016049
2008	backup	UNAVAILABLE	\N	2026-08-19 17:14:26.016049
2009	sentry	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2010	openai	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2011	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:14:26.016049
2012	simulation	HEALTHY	\N	2026-08-19 17:14:26.016049
2013	application	HEALTHY	4.5	2026-08-19 17:14:26.016049
2058	database	HEALTHY	1	2026-08-19 17:16:56.278995
2059	redis	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2060	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2061	celery	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2062	email	HEALTHY	\N	2026-08-19 17:16:56.278995
2063	backup	UNAVAILABLE	\N	2026-08-19 17:16:56.278995
2064	sentry	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2065	openai	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2066	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:16:56.278995
2067	simulation	HEALTHY	\N	2026-08-19 17:16:56.278995
2068	application	HEALTHY	4.5	2026-08-19 17:16:56.278995
2069	database	HEALTHY	1	2026-08-19 17:17:26.301842
2070	redis	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2071	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2072	celery	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2073	email	HEALTHY	\N	2026-08-19 17:17:26.301842
2074	backup	UNAVAILABLE	\N	2026-08-19 17:17:26.301842
2075	sentry	NOT_CONFIGURED	\N	2026-08-19 17:17:26.301842
2076	openai	NOT_CONFIGURED	\N	2026-08-19 17:17:26.302842
2077	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:17:26.302842
2078	simulation	HEALTHY	\N	2026-08-19 17:17:26.302842
2079	application	HEALTHY	4.5	2026-08-19 17:17:26.302842
2091	database	HEALTHY	0	2026-08-19 17:18:26.381749
2092	redis	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2093	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2094	celery	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2095	email	HEALTHY	\N	2026-08-19 17:18:26.382749
2096	backup	UNAVAILABLE	\N	2026-08-19 17:18:26.382749
2097	sentry	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2098	openai	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2099	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:18:26.382749
2100	simulation	HEALTHY	\N	2026-08-19 17:18:26.382749
2101	application	HEALTHY	4.5	2026-08-19 17:18:26.382749
2806	database	HEALTHY	20	2026-08-19 18:16:14.352338
2807	redis	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2808	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2809	celery	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2810	email	HEALTHY	\N	2026-08-19 18:16:14.352338
2811	backup	UNAVAILABLE	\N	2026-08-19 18:16:14.352338
2812	sentry	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2813	openai	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2814	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:16:14.352338
2815	simulation	HEALTHY	\N	2026-08-19 18:16:14.352338
2816	application	HEALTHY	4.5	2026-08-19 18:16:14.352338
2817	database	HEALTHY	0	2026-08-19 18:16:44.445018
2818	redis	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2819	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2820	celery	NOT_CONFIGURED	\N	2026-08-19 18:16:44.445018
2821	email	HEALTHY	\N	2026-08-19 18:16:44.445018
2822	backup	UNAVAILABLE	\N	2026-08-19 18:16:44.445018
2823	sentry	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2824	openai	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2825	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:16:44.446016
2826	simulation	HEALTHY	\N	2026-08-19 18:16:44.446016
2827	application	HEALTHY	4.5	2026-08-19 18:16:44.446016
2839	database	HEALTHY	1	2026-08-19 18:17:44.557355
2840	redis	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2841	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2842	celery	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2843	email	HEALTHY	\N	2026-08-19 18:17:44.557355
2844	backup	UNAVAILABLE	\N	2026-08-19 18:17:44.557355
2845	sentry	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2846	openai	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2847	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:17:44.557355
2848	simulation	HEALTHY	\N	2026-08-19 18:17:44.557355
2849	application	HEALTHY	4.5	2026-08-19 18:17:44.557355
2014	database	HEALTHY	1	2026-08-19 17:14:56.049366
2015	redis	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2016	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2017	celery	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2018	email	HEALTHY	\N	2026-08-19 17:14:56.049366
2019	backup	UNAVAILABLE	\N	2026-08-19 17:14:56.049366
2020	sentry	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2021	openai	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2022	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:14:56.049366
2023	simulation	HEALTHY	\N	2026-08-19 17:14:56.049366
2024	application	HEALTHY	4.5	2026-08-19 17:14:56.049366
2025	database	HEALTHY	0	2026-08-19 17:15:26.077115
2026	redis	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2027	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2028	celery	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2029	email	HEALTHY	\N	2026-08-19 17:15:26.077115
2030	backup	UNAVAILABLE	\N	2026-08-19 17:15:26.077115
2031	sentry	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2032	openai	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2033	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:15:26.077115
2034	simulation	HEALTHY	\N	2026-08-19 17:15:26.077115
2035	application	HEALTHY	4.5	2026-08-19 17:15:26.077115
2036	database	HEALTHY	0.96	2026-08-19 17:15:56.167661
2037	redis	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2038	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2039	celery	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2040	email	HEALTHY	\N	2026-08-19 17:15:56.167661
2041	backup	UNAVAILABLE	\N	2026-08-19 17:15:56.167661
2042	sentry	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2043	openai	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2044	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:15:56.167661
2045	simulation	HEALTHY	\N	2026-08-19 17:15:56.167661
2046	application	HEALTHY	4.5	2026-08-19 17:15:56.167661
2080	database	HEALTHY	0	2026-08-19 17:17:56.344446
2081	redis	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2082	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2083	celery	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2084	email	HEALTHY	\N	2026-08-19 17:17:56.344446
2085	backup	UNAVAILABLE	\N	2026-08-19 17:17:56.344446
2086	sentry	NOT_CONFIGURED	\N	2026-08-19 17:17:56.344446
2087	openai	NOT_CONFIGURED	\N	2026-08-19 17:17:56.345442
2088	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:17:56.345442
2089	simulation	HEALTHY	\N	2026-08-19 17:17:56.345442
2090	application	HEALTHY	4.5	2026-08-19 17:17:56.345442
2113	database	HEALTHY	1	2026-08-19 17:19:26.448016
2114	redis	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2115	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2116	celery	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2117	email	HEALTHY	\N	2026-08-19 17:19:26.449055
2118	backup	UNAVAILABLE	\N	2026-08-19 17:19:26.449055
2119	sentry	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2120	openai	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2121	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:19:26.449055
2122	simulation	HEALTHY	\N	2026-08-19 17:19:26.449055
2123	application	HEALTHY	4.5	2026-08-19 17:19:26.449055
2124	database	HEALTHY	0	2026-08-19 17:19:56.479634
2125	redis	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2126	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2127	celery	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2128	email	HEALTHY	\N	2026-08-19 17:19:56.479634
2129	backup	UNAVAILABLE	\N	2026-08-19 17:19:56.479634
2130	sentry	NOT_CONFIGURED	\N	2026-08-19 17:19:56.479634
2131	openai	NOT_CONFIGURED	\N	2026-08-19 17:19:56.480636
2132	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:19:56.480636
2133	simulation	HEALTHY	\N	2026-08-19 17:19:56.480636
2134	application	HEALTHY	4.5	2026-08-19 17:19:56.480636
2828	database	HEALTHY	0	2026-08-19 18:17:14.488657
2829	redis	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2830	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2831	celery	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2832	email	HEALTHY	\N	2026-08-19 18:17:14.488657
2833	backup	UNAVAILABLE	\N	2026-08-19 18:17:14.488657
2834	sentry	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2835	openai	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2836	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:17:14.488657
2837	simulation	HEALTHY	\N	2026-08-19 18:17:14.488657
2838	application	HEALTHY	4.5	2026-08-19 18:17:14.488657
2102	database	HEALTHY	1	2026-08-19 17:18:56.413112
2103	redis	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2104	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2105	celery	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2106	email	HEALTHY	\N	2026-08-19 17:18:56.414112
2107	backup	UNAVAILABLE	\N	2026-08-19 17:18:56.414112
2108	sentry	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2109	openai	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2110	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:18:56.414112
2111	simulation	HEALTHY	\N	2026-08-19 17:18:56.414112
2112	application	HEALTHY	4.5	2026-08-19 17:18:56.414112
2135	database	HEALTHY	1	2026-08-19 17:20:26.50915
2136	redis	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2137	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2138	celery	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2139	email	HEALTHY	\N	2026-08-19 17:20:26.50915
2140	backup	UNAVAILABLE	\N	2026-08-19 17:20:26.50915
2141	sentry	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2142	openai	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2143	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:20:26.50915
2144	simulation	HEALTHY	\N	2026-08-19 17:20:26.50915
2145	application	HEALTHY	4.5	2026-08-19 17:20:26.510152
2146	database	HEALTHY	0	2026-08-19 17:20:56.545429
2147	redis	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2148	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2149	celery	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2150	email	HEALTHY	\N	2026-08-19 17:20:56.545429
2151	backup	UNAVAILABLE	\N	2026-08-19 17:20:56.545429
2152	sentry	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2153	openai	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2154	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:20:56.545429
2155	simulation	HEALTHY	\N	2026-08-19 17:20:56.545429
2156	application	HEALTHY	4.5	2026-08-19 17:20:56.545429
2157	database	HEALTHY	1.99	2026-08-19 17:21:26.621726
2158	redis	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2159	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2160	celery	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2161	email	HEALTHY	\N	2026-08-19 17:21:26.621726
2162	backup	UNAVAILABLE	\N	2026-08-19 17:21:26.621726
2163	sentry	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2164	openai	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2165	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:21:26.621726
2166	simulation	HEALTHY	\N	2026-08-19 17:21:26.623365
2167	application	HEALTHY	4.5	2026-08-19 17:21:26.623365
2168	database	HEALTHY	0.95	2026-08-19 17:21:56.690583
2169	redis	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2170	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2171	celery	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2172	email	HEALTHY	\N	2026-08-19 17:21:56.690583
2173	backup	UNAVAILABLE	\N	2026-08-19 17:21:56.690583
2174	sentry	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2175	openai	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2176	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:21:56.690583
2177	simulation	HEALTHY	\N	2026-08-19 17:21:56.690583
2178	application	HEALTHY	4.5	2026-08-19 17:21:56.691599
2179	database	HEALTHY	0	2026-08-19 17:22:26.735083
2180	redis	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2181	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2182	celery	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2183	email	HEALTHY	\N	2026-08-19 17:22:26.735083
2184	backup	UNAVAILABLE	\N	2026-08-19 17:22:26.735083
2185	sentry	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2186	openai	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2187	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:22:26.735083
2188	simulation	HEALTHY	\N	2026-08-19 17:22:26.735083
2189	application	HEALTHY	4.5	2026-08-19 17:22:26.735083
2190	database	HEALTHY	0	2026-08-19 17:22:56.766909
2191	redis	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2192	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2193	celery	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2194	email	HEALTHY	\N	2026-08-19 17:22:56.766909
2195	backup	UNAVAILABLE	\N	2026-08-19 17:22:56.766909
2196	sentry	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2197	openai	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2198	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:22:56.766909
2199	simulation	HEALTHY	\N	2026-08-19 17:22:56.766909
2200	application	HEALTHY	4.5	2026-08-19 17:22:56.766909
2201	database	HEALTHY	0	2026-08-19 17:23:26.808649
2202	redis	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2203	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2204	celery	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2205	email	HEALTHY	\N	2026-08-19 17:23:26.808649
2206	backup	UNAVAILABLE	\N	2026-08-19 17:23:26.808649
2207	sentry	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2208	openai	NOT_CONFIGURED	\N	2026-08-19 17:23:26.808649
2209	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:23:26.809651
2210	simulation	HEALTHY	\N	2026-08-19 17:23:26.809651
2211	application	HEALTHY	4.5	2026-08-19 17:23:26.809651
2212	database	HEALTHY	1	2026-08-19 17:23:56.848013
2213	redis	NOT_CONFIGURED	\N	2026-08-19 17:23:56.848013
2214	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2215	celery	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2216	email	HEALTHY	\N	2026-08-19 17:23:56.849295
2217	backup	UNAVAILABLE	\N	2026-08-19 17:23:56.849295
2218	sentry	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2219	openai	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2220	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:23:56.849295
2221	simulation	HEALTHY	\N	2026-08-19 17:23:56.849295
2222	application	HEALTHY	4.5	2026-08-19 17:23:56.849295
2223	database	HEALTHY	1.05	2026-08-19 17:24:26.879047
2224	redis	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2225	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2226	celery	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2227	email	HEALTHY	\N	2026-08-19 17:24:26.880047
2228	backup	UNAVAILABLE	\N	2026-08-19 17:24:26.880047
2229	sentry	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2230	openai	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2231	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:24:26.880047
2232	simulation	HEALTHY	\N	2026-08-19 17:24:26.880047
2233	application	HEALTHY	4.5	2026-08-19 17:24:26.880047
2234	database	HEALTHY	1	2026-08-19 17:24:56.918597
2235	redis	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2236	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2237	celery	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2238	email	HEALTHY	\N	2026-08-19 17:24:56.918597
2239	backup	UNAVAILABLE	\N	2026-08-19 17:24:56.918597
2240	sentry	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2241	openai	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2242	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:24:56.918597
2243	simulation	HEALTHY	\N	2026-08-19 17:24:56.918597
2244	application	HEALTHY	4.5	2026-08-19 17:24:56.918597
2245	database	HEALTHY	0	2026-08-19 17:25:26.950968
2246	redis	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2247	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2248	celery	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2249	email	HEALTHY	\N	2026-08-19 17:25:26.950968
2250	backup	UNAVAILABLE	\N	2026-08-19 17:25:26.950968
2251	sentry	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2252	openai	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2253	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:25:26.950968
2254	simulation	HEALTHY	\N	2026-08-19 17:25:26.950968
2255	application	HEALTHY	4.5	2026-08-19 17:25:26.950968
2256	database	HEALTHY	1	2026-08-19 17:25:56.983312
2257	redis	NOT_CONFIGURED	\N	2026-08-19 17:25:56.983312
2258	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2259	celery	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2260	email	HEALTHY	\N	2026-08-19 17:25:56.984315
2261	backup	UNAVAILABLE	\N	2026-08-19 17:25:56.984315
2262	sentry	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2263	openai	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2264	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:25:56.984315
2265	simulation	HEALTHY	\N	2026-08-19 17:25:56.984315
2266	application	HEALTHY	4.5	2026-08-19 17:25:56.984315
2850	database	HEALTHY	1	2026-08-19 18:18:14.612283
2851	redis	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2852	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2853	celery	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2854	email	HEALTHY	\N	2026-08-19 18:18:14.612283
2855	backup	UNAVAILABLE	\N	2026-08-19 18:18:14.612283
2856	sentry	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2857	openai	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2858	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:18:14.612283
2859	simulation	HEALTHY	\N	2026-08-19 18:18:14.613285
2860	application	HEALTHY	4.5	2026-08-19 18:18:14.613285
2267	database	HEALTHY	0	2026-08-19 17:26:27.022829
2268	redis	NOT_CONFIGURED	\N	2026-08-19 17:26:27.022829
2269	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:26:27.022829
2270	celery	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2271	email	HEALTHY	\N	2026-08-19 17:26:27.023818
2272	backup	UNAVAILABLE	\N	2026-08-19 17:26:27.023818
2273	sentry	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2274	openai	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2275	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:26:27.023818
2276	simulation	HEALTHY	\N	2026-08-19 17:26:27.023818
2277	application	HEALTHY	4.5	2026-08-19 17:26:27.023818
2872	database	HEALTHY	0	2026-08-19 18:19:14.677312
2873	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2874	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2875	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2876	email	HEALTHY	\N	2026-08-19 18:19:14.677312
2877	backup	UNAVAILABLE	\N	2026-08-19 18:19:14.677312
2878	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2879	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2880	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:14.677312
2881	simulation	HEALTHY	\N	2026-08-19 18:19:14.677312
2882	application	HEALTHY	4.5	2026-08-19 18:19:14.677312
2278	database	HEALTHY	0	2026-08-19 17:26:57.054833
2279	redis	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2280	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2281	celery	NOT_CONFIGURED	\N	2026-08-19 17:26:57.054833
2282	email	HEALTHY	\N	2026-08-19 17:26:57.054833
2283	backup	UNAVAILABLE	\N	2026-08-19 17:26:57.054833
2284	sentry	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2285	openai	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2286	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:26:57.055832
2287	simulation	HEALTHY	\N	2026-08-19 17:26:57.055832
2288	application	HEALTHY	4.5	2026-08-19 17:26:57.055832
2289	database	HEALTHY	1.37	2026-08-19 17:27:27.103673
2290	redis	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2291	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2292	celery	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2293	email	HEALTHY	\N	2026-08-19 17:27:27.103673
2294	backup	UNAVAILABLE	\N	2026-08-19 17:27:27.103673
2295	sentry	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2296	openai	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2297	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:27:27.103673
2298	simulation	HEALTHY	\N	2026-08-19 17:27:27.103673
2299	application	HEALTHY	4.5	2026-08-19 17:27:27.103673
2300	database	HEALTHY	2.02	2026-08-19 17:27:57.169766
2301	redis	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2302	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2303	celery	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2304	email	HEALTHY	\N	2026-08-19 17:27:57.169766
2305	backup	UNAVAILABLE	\N	2026-08-19 17:27:57.169766
2306	sentry	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2307	openai	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2308	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:27:57.169766
2309	simulation	HEALTHY	\N	2026-08-19 17:27:57.169766
2310	application	HEALTHY	4.5	2026-08-19 17:27:57.169766
2344	database	HEALTHY	0	2026-08-19 17:29:57.346478
2345	redis	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2346	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2347	celery	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2348	email	HEALTHY	\N	2026-08-19 17:29:57.346478
2349	backup	UNAVAILABLE	\N	2026-08-19 17:29:57.346478
2350	sentry	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2351	openai	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2352	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:29:57.346478
2353	simulation	HEALTHY	\N	2026-08-19 17:29:57.346478
2354	application	HEALTHY	4.5	2026-08-19 17:29:57.346478
2366	database	HEALTHY	1	2026-08-19 17:30:57.403266
2367	redis	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2368	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2369	celery	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2370	email	HEALTHY	\N	2026-08-19 17:30:57.404307
2371	backup	UNAVAILABLE	\N	2026-08-19 17:30:57.404307
2372	sentry	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2373	openai	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2374	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:30:57.404307
2375	simulation	HEALTHY	\N	2026-08-19 17:30:57.404307
2376	application	HEALTHY	4.5	2026-08-19 17:30:57.404307
2883	database	HEALTHY	0	2026-08-19 18:19:23.320233
2884	redis	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2885	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2886	celery	NOT_CONFIGURED	\N	2026-08-19 18:19:23.320233
2887	email	HEALTHY	\N	2026-08-19 18:19:23.321235
2888	backup	HEALTHY	\N	2026-08-19 18:19:23.321235
2889	sentry	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2890	openai	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2891	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:19:23.321235
2892	simulation	HEALTHY	\N	2026-08-19 18:19:23.321235
2893	application	HEALTHY	4.5	2026-08-19 18:19:23.321235
2311	database	HEALTHY	1	2026-08-19 17:28:27.211457
2312	redis	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2313	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2314	celery	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2315	email	HEALTHY	\N	2026-08-19 17:28:27.212453
2316	backup	UNAVAILABLE	\N	2026-08-19 17:28:27.212453
2317	sentry	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2318	openai	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2319	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:28:27.212453
2320	simulation	HEALTHY	\N	2026-08-19 17:28:27.212453
2321	application	HEALTHY	4.5	2026-08-19 17:28:27.212453
2322	database	HEALTHY	1.02	2026-08-19 17:28:57.260897
2323	redis	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2324	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2325	celery	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2326	email	HEALTHY	\N	2026-08-19 17:28:57.260897
2327	backup	UNAVAILABLE	\N	2026-08-19 17:28:57.260897
2328	sentry	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2329	openai	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2330	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:28:57.260897
2331	simulation	HEALTHY	\N	2026-08-19 17:28:57.260897
2332	application	HEALTHY	4.5	2026-08-19 17:28:57.260897
2333	database	HEALTHY	0.99	2026-08-19 17:29:27.314667
2334	redis	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2335	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2336	celery	NOT_CONFIGURED	\N	2026-08-19 17:29:27.314667
2337	email	HEALTHY	\N	2026-08-19 17:29:27.314667
2338	backup	UNAVAILABLE	\N	2026-08-19 17:29:27.315669
2339	sentry	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2340	openai	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2341	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:29:27.315669
2342	simulation	HEALTHY	\N	2026-08-19 17:29:27.315669
2343	application	HEALTHY	4.5	2026-08-19 17:29:27.315669
2377	database	HEALTHY	1	2026-08-19 17:31:27.440109
2378	redis	NOT_CONFIGURED	\N	2026-08-19 17:31:27.440109
2379	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2380	celery	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2381	email	HEALTHY	\N	2026-08-19 17:31:27.441127
2382	backup	UNAVAILABLE	\N	2026-08-19 17:31:27.441127
2383	sentry	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2384	openai	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2385	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:31:27.441127
2386	simulation	HEALTHY	\N	2026-08-19 17:31:27.441127
2387	application	HEALTHY	4.5	2026-08-19 17:31:27.441127
2388	database	HEALTHY	1	2026-08-19 17:31:57.466346
2389	redis	NOT_CONFIGURED	\N	2026-08-19 17:31:57.466346
2390	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2391	celery	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2392	email	HEALTHY	\N	2026-08-19 17:31:57.467337
2393	backup	UNAVAILABLE	\N	2026-08-19 17:31:57.467337
2394	sentry	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2395	openai	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467337
2396	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:31:57.467826
2397	simulation	HEALTHY	\N	2026-08-19 17:31:57.467826
2398	application	HEALTHY	4.5	2026-08-19 17:31:57.467826
2355	database	HEALTHY	1.01	2026-08-19 17:30:27.373681
2356	redis	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2357	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2358	celery	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2359	email	HEALTHY	\N	2026-08-19 17:30:27.373681
2360	backup	UNAVAILABLE	\N	2026-08-19 17:30:27.373681
2361	sentry	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2362	openai	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2363	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:30:27.373681
2364	simulation	HEALTHY	\N	2026-08-19 17:30:27.373681
2365	application	HEALTHY	4.5	2026-08-19 17:30:27.373681
2399	database	HEALTHY	0	2026-08-19 17:32:27.491365
2400	redis	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2401	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2402	celery	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2403	email	HEALTHY	\N	2026-08-19 17:32:27.492366
2404	backup	UNAVAILABLE	\N	2026-08-19 17:32:27.492366
2405	sentry	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2406	openai	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2407	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:32:27.492366
2408	simulation	HEALTHY	\N	2026-08-19 17:32:27.492366
2409	application	HEALTHY	4.5	2026-08-19 17:32:27.492366
2410	database	HEALTHY	0	2026-08-19 17:32:57.531701
2411	redis	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2412	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2413	celery	NOT_CONFIGURED	\N	2026-08-19 17:32:57.531701
2414	email	HEALTHY	\N	2026-08-19 17:32:57.531701
2415	backup	UNAVAILABLE	\N	2026-08-19 17:32:57.532697
2416	sentry	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2417	openai	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2418	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:32:57.532697
2419	simulation	HEALTHY	\N	2026-08-19 17:32:57.532697
2420	application	HEALTHY	4.5	2026-08-19 17:32:57.532697
2421	database	HEALTHY	1	2026-08-19 17:33:27.564793
2422	redis	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2423	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2424	celery	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2425	email	HEALTHY	\N	2026-08-19 17:33:27.564793
2426	backup	UNAVAILABLE	\N	2026-08-19 17:33:27.564793
2427	sentry	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2428	openai	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2429	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:33:27.564793
2430	simulation	HEALTHY	\N	2026-08-19 17:33:27.564793
2431	application	HEALTHY	4.5	2026-08-19 17:33:27.565787
2432	database	HEALTHY	0	2026-08-19 17:33:57.596783
2433	redis	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2434	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2435	celery	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2436	email	HEALTHY	\N	2026-08-19 17:33:57.596783
2437	backup	UNAVAILABLE	\N	2026-08-19 17:33:57.596783
2438	sentry	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2439	openai	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2440	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:33:57.596783
2441	simulation	HEALTHY	\N	2026-08-19 17:33:57.596783
2442	application	HEALTHY	4.5	2026-08-19 17:33:57.596783
2443	database	HEALTHY	0	2026-08-19 17:34:27.650013
2444	redis	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2445	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2446	celery	NOT_CONFIGURED	\N	2026-08-19 17:34:27.650013
2447	email	HEALTHY	\N	2026-08-19 17:34:27.651012
2448	backup	UNAVAILABLE	\N	2026-08-19 17:34:27.651012
2449	sentry	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2450	openai	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2451	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:34:27.651012
2452	simulation	HEALTHY	\N	2026-08-19 17:34:27.651012
2453	application	HEALTHY	4.5	2026-08-19 17:34:27.651012
2454	database	HEALTHY	1.11	2026-08-19 17:34:57.714404
2455	redis	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2456	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2457	celery	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2458	email	HEALTHY	\N	2026-08-19 17:34:57.714404
2459	backup	UNAVAILABLE	\N	2026-08-19 17:34:57.714404
2460	sentry	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2461	openai	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2462	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:34:57.714404
2463	simulation	HEALTHY	\N	2026-08-19 17:34:57.714404
2464	application	HEALTHY	4.5	2026-08-19 17:34:57.714404
2465	database	HEALTHY	1	2026-08-19 17:35:27.773865
2466	redis	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2467	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2468	celery	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2469	email	HEALTHY	\N	2026-08-19 17:35:27.773865
2470	backup	UNAVAILABLE	\N	2026-08-19 17:35:27.773865
2471	sentry	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2472	openai	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2473	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:35:27.773865
2474	simulation	HEALTHY	\N	2026-08-19 17:35:27.773865
2475	application	HEALTHY	4.5	2026-08-19 17:35:27.773865
2476	database	HEALTHY	1.01	2026-08-19 17:35:57.808189
2477	redis	NOT_CONFIGURED	\N	2026-08-19 17:35:57.808189
2478	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2479	celery	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2480	email	HEALTHY	\N	2026-08-19 17:35:57.80919
2481	backup	UNAVAILABLE	\N	2026-08-19 17:35:57.80919
2482	sentry	NOT_CONFIGURED	\N	2026-08-19 17:35:57.80919
2483	openai	NOT_CONFIGURED	\N	2026-08-19 17:35:57.81019
2484	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:35:57.81019
2485	simulation	HEALTHY	\N	2026-08-19 17:35:57.81019
2486	application	HEALTHY	4.5	2026-08-19 17:35:57.81019
2487	database	HEALTHY	1	2026-08-19 17:36:27.83402
2488	redis	NOT_CONFIGURED	\N	2026-08-19 17:36:27.83402
2489	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2490	celery	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2491	email	HEALTHY	\N	2026-08-19 17:36:27.835025
2492	backup	UNAVAILABLE	\N	2026-08-19 17:36:27.835025
2493	sentry	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2494	openai	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2495	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:36:27.835025
2496	simulation	HEALTHY	\N	2026-08-19 17:36:27.835025
2497	application	HEALTHY	4.5	2026-08-19 17:36:27.835025
2498	database	HEALTHY	1.53	2026-08-19 17:36:57.871032
2499	redis	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2500	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2501	celery	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2502	email	HEALTHY	\N	2026-08-19 17:36:57.871032
2503	backup	UNAVAILABLE	\N	2026-08-19 17:36:57.871032
2504	sentry	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2505	openai	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2506	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:36:57.871032
2507	simulation	HEALTHY	\N	2026-08-19 17:36:57.871032
2508	application	HEALTHY	4.5	2026-08-19 17:36:57.871032
2509	database	HEALTHY	1	2026-08-19 17:37:27.902669
2510	redis	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2511	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2512	celery	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2513	email	HEALTHY	\N	2026-08-19 17:37:27.902669
2514	backup	UNAVAILABLE	\N	2026-08-19 17:37:27.902669
2515	sentry	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2516	openai	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2517	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:37:27.902669
2518	simulation	HEALTHY	\N	2026-08-19 17:37:27.903673
2519	application	HEALTHY	4.5	2026-08-19 17:37:27.903673
2520	database	HEALTHY	0	2026-08-19 17:37:57.944225
2521	redis	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2522	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2523	celery	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2524	email	HEALTHY	\N	2026-08-19 17:37:57.945225
2525	backup	UNAVAILABLE	\N	2026-08-19 17:37:57.945225
2526	sentry	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2527	openai	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2528	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:37:57.945225
2529	simulation	HEALTHY	\N	2026-08-19 17:37:57.945225
2530	application	HEALTHY	4.5	2026-08-19 17:37:57.945225
2531	database	HEALTHY	0	2026-08-19 17:38:27.967346
2532	redis	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2533	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2534	celery	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2535	email	HEALTHY	\N	2026-08-19 17:38:27.967346
2536	backup	UNAVAILABLE	\N	2026-08-19 17:38:27.967346
2537	sentry	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2538	openai	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2539	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:38:27.967346
2540	simulation	HEALTHY	\N	2026-08-19 17:38:27.967346
2541	application	HEALTHY	4.5	2026-08-19 17:38:27.968347
2542	database	HEALTHY	1.98	2026-08-19 17:38:58.030375
2543	redis	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2544	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2545	celery	NOT_CONFIGURED	\N	2026-08-19 17:38:58.030375
2546	email	HEALTHY	\N	2026-08-19 17:38:58.031351
2547	backup	UNAVAILABLE	\N	2026-08-19 17:38:58.031351
2548	sentry	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2549	openai	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2550	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:38:58.031351
2551	simulation	HEALTHY	\N	2026-08-19 17:38:58.031351
2552	application	HEALTHY	4.5	2026-08-19 17:38:58.031351
2553	database	HEALTHY	1.98	2026-08-19 17:39:28.098572
2554	redis	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2555	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2556	celery	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2557	email	HEALTHY	\N	2026-08-19 17:39:28.09958
2558	backup	UNAVAILABLE	\N	2026-08-19 17:39:28.09958
2559	sentry	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2560	openai	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2561	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:39:28.09958
2562	simulation	HEALTHY	\N	2026-08-19 17:39:28.09958
2563	application	HEALTHY	4.5	2026-08-19 17:39:28.09958
2564	database	HEALTHY	2.05	2026-08-19 17:39:58.159519
2565	redis	NOT_CONFIGURED	\N	2026-08-19 17:39:58.159519
2566	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2567	celery	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2568	email	HEALTHY	\N	2026-08-19 17:39:58.160514
2569	backup	UNAVAILABLE	\N	2026-08-19 17:39:58.160514
2570	sentry	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2571	openai	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2572	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:39:58.160514
2573	simulation	HEALTHY	\N	2026-08-19 17:39:58.160514
2574	application	HEALTHY	4.5	2026-08-19 17:39:58.160514
2575	database	HEALTHY	0.99	2026-08-19 17:40:28.243079
2576	redis	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2577	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2578	celery	NOT_CONFIGURED	\N	2026-08-19 17:40:28.243079
2579	email	HEALTHY	\N	2026-08-19 17:40:28.244076
2580	backup	UNAVAILABLE	\N	2026-08-19 17:40:28.244076
2581	sentry	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2582	openai	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2583	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:40:28.244076
2584	simulation	HEALTHY	\N	2026-08-19 17:40:28.244076
2585	application	HEALTHY	4.5	2026-08-19 17:40:28.244076
2586	database	HEALTHY	0	2026-08-19 17:40:58.284176
2587	redis	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2588	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2589	celery	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2590	email	HEALTHY	\N	2026-08-19 17:40:58.285177
2591	backup	UNAVAILABLE	\N	2026-08-19 17:40:58.285177
2592	sentry	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2593	openai	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2594	cloudflare	NOT_CONFIGURED	\N	2026-08-19 17:40:58.285177
2595	simulation	HEALTHY	\N	2026-08-19 17:40:58.285177
2596	application	HEALTHY	4.5	2026-08-19 17:40:58.285177
2597	database	HEALTHY	1	2026-08-19 18:03:54.409594
2598	redis	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2599	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2600	celery	NOT_CONFIGURED	\N	2026-08-19 18:03:54.409594
2601	email	HEALTHY	\N	2026-08-19 18:03:54.409594
2602	backup	UNAVAILABLE	\N	2026-08-19 18:03:54.409594
2603	sentry	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2604	openai	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2605	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:03:54.41064
2606	simulation	HEALTHY	\N	2026-08-19 18:03:54.41064
2607	application	HEALTHY	4.5	2026-08-19 18:03:54.41064
2608	database	HEALTHY	1	2026-08-19 18:06:56.751729
2609	redis	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2610	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2611	celery	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2612	email	HEALTHY	\N	2026-08-19 18:06:56.751729
2613	backup	UNAVAILABLE	\N	2026-08-19 18:06:56.751729
2614	sentry	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2615	openai	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2616	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:06:56.751729
2617	simulation	HEALTHY	\N	2026-08-19 18:06:56.751729
2618	application	HEALTHY	4.5	2026-08-19 18:06:56.751729
2619	database	HEALTHY	1.03	2026-08-19 18:07:26.79446
2620	redis	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2621	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2622	celery	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2623	email	HEALTHY	\N	2026-08-19 18:07:26.79446
2624	backup	UNAVAILABLE	\N	2026-08-19 18:07:26.79446
2625	sentry	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2626	openai	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2627	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:07:26.79446
2628	simulation	HEALTHY	\N	2026-08-19 18:07:26.79446
2629	application	HEALTHY	4.5	2026-08-19 18:07:26.79446
2630	database	HEALTHY	1.01	2026-08-19 18:07:56.8419
2631	redis	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2632	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2633	celery	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2634	email	HEALTHY	\N	2026-08-19 18:07:56.8419
2635	backup	UNAVAILABLE	\N	2026-08-19 18:07:56.8419
2636	sentry	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2637	openai	NOT_CONFIGURED	\N	2026-08-19 18:07:56.8419
2638	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:07:56.842919
2639	simulation	HEALTHY	\N	2026-08-19 18:07:56.842919
2640	application	HEALTHY	4.5	2026-08-19 18:07:56.842919
2641	database	HEALTHY	0.77	2026-08-19 18:08:26.885614
2642	redis	NOT_CONFIGURED	\N	2026-08-19 18:08:26.885614
2643	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2644	celery	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2645	email	HEALTHY	\N	2026-08-19 18:08:26.886594
2646	backup	UNAVAILABLE	\N	2026-08-19 18:08:26.886594
2647	sentry	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2648	openai	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2649	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:08:26.886594
2650	simulation	HEALTHY	\N	2026-08-19 18:08:26.886594
2651	application	HEALTHY	4.5	2026-08-19 18:08:26.886594
2652	database	HEALTHY	1	2026-08-19 18:08:56.920829
2653	redis	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2654	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2655	celery	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2656	email	HEALTHY	\N	2026-08-19 18:08:56.92183
2657	backup	UNAVAILABLE	\N	2026-08-19 18:08:56.92183
2658	sentry	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2659	openai	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2660	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:08:56.92183
2661	simulation	HEALTHY	\N	2026-08-19 18:08:56.92183
2662	application	HEALTHY	4.5	2026-08-19 18:08:56.92183
2663	database	HEALTHY	0	2026-08-19 18:09:26.951583
2664	redis	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2665	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2666	celery	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2667	email	HEALTHY	\N	2026-08-19 18:09:26.951583
2668	backup	UNAVAILABLE	\N	2026-08-19 18:09:26.951583
2669	sentry	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2670	openai	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2671	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:09:26.951583
2672	simulation	HEALTHY	\N	2026-08-19 18:09:26.951583
2673	application	HEALTHY	4.5	2026-08-19 18:09:26.951583
2674	database	HEALTHY	1	2026-08-19 18:09:56.980211
2675	redis	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2676	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2677	celery	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2678	email	HEALTHY	\N	2026-08-19 18:09:56.980211
2679	backup	UNAVAILABLE	\N	2026-08-19 18:09:56.980211
2680	sentry	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2681	openai	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2682	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:09:56.980211
2683	simulation	HEALTHY	\N	2026-08-19 18:09:56.980211
2684	application	HEALTHY	4.5	2026-08-19 18:09:56.980211
2685	database	HEALTHY	0	2026-08-19 18:10:27.031496
2686	redis	NOT_CONFIGURED	\N	2026-08-19 18:10:27.031496
2687	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:10:27.031496
2688	celery	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2689	email	HEALTHY	\N	2026-08-19 18:10:27.032495
2690	backup	UNAVAILABLE	\N	2026-08-19 18:10:27.032495
2691	sentry	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2692	openai	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2693	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:10:27.032495
2694	simulation	HEALTHY	\N	2026-08-19 18:10:27.032495
2695	application	HEALTHY	4.5	2026-08-19 18:10:27.032495
2696	database	HEALTHY	1.01	2026-08-19 18:10:57.109094
2697	redis	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2698	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2699	celery	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2700	email	HEALTHY	\N	2026-08-19 18:10:57.109094
2701	backup	UNAVAILABLE	\N	2026-08-19 18:10:57.109094
2702	sentry	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2703	openai	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2704	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:10:57.109094
2705	simulation	HEALTHY	\N	2026-08-19 18:10:57.109094
2706	application	HEALTHY	4.5	2026-08-19 18:10:57.109094
2707	database	HEALTHY	0	2026-08-19 18:11:27.163317
2708	redis	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2709	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2710	celery	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2711	email	HEALTHY	\N	2026-08-19 18:11:27.163317
2712	backup	UNAVAILABLE	\N	2026-08-19 18:11:27.163317
2713	sentry	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2714	openai	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2715	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:11:27.163317
2716	simulation	HEALTHY	\N	2026-08-19 18:11:27.163317
2717	application	HEALTHY	4.5	2026-08-19 18:11:27.163317
2718	database	HEALTHY	1	2026-08-19 18:11:57.189044
2719	redis	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2720	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2721	celery	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2722	email	HEALTHY	\N	2026-08-19 18:11:57.189044
2723	backup	UNAVAILABLE	\N	2026-08-19 18:11:57.189044
2724	sentry	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2725	openai	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2726	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:11:57.189044
2727	simulation	HEALTHY	\N	2026-08-19 18:11:57.189044
2728	application	HEALTHY	4.5	2026-08-19 18:11:57.189044
2729	database	HEALTHY	11.29	2026-08-19 18:12:27.294227
2730	redis	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2731	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2732	celery	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2733	email	HEALTHY	\N	2026-08-19 18:12:27.295229
2734	backup	UNAVAILABLE	\N	2026-08-19 18:12:27.295229
2735	sentry	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2736	openai	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2737	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:12:27.295229
2738	simulation	HEALTHY	\N	2026-08-19 18:12:27.295229
2739	application	HEALTHY	4.5	2026-08-19 18:12:27.295229
2740	database	HEALTHY	0.99	2026-08-19 18:12:57.319008
2741	redis	NOT_CONFIGURED	\N	2026-08-19 18:12:57.319008
2742	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:12:57.319008
2743	celery	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2744	email	HEALTHY	\N	2026-08-19 18:12:57.320004
2745	backup	UNAVAILABLE	\N	2026-08-19 18:12:57.320004
2746	sentry	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2747	openai	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2748	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:12:57.320004
2749	simulation	HEALTHY	\N	2026-08-19 18:12:57.320004
2750	application	HEALTHY	4.5	2026-08-19 18:12:57.320004
2751	database	HEALTHY	1.13	2026-08-19 18:13:27.34698
2752	redis	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2753	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2754	celery	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2755	email	HEALTHY	\N	2026-08-19 18:13:27.348433
2756	backup	UNAVAILABLE	\N	2026-08-19 18:13:27.348433
2757	sentry	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2758	openai	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2759	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:13:27.348433
2760	simulation	HEALTHY	\N	2026-08-19 18:13:27.348433
2761	application	HEALTHY	4.5	2026-08-19 18:13:27.348433
2762	database	HEALTHY	3.51	2026-08-19 18:13:57.443364
2763	redis	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2764	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2765	celery	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2766	email	HEALTHY	\N	2026-08-19 18:13:57.443364
2767	backup	UNAVAILABLE	\N	2026-08-19 18:13:57.443364
2768	sentry	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2769	openai	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2770	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:13:57.443364
2771	simulation	HEALTHY	\N	2026-08-19 18:13:57.443364
2772	application	HEALTHY	4.5	2026-08-19 18:13:57.443364
2773	database	HEALTHY	1	2026-08-19 18:14:44.167485
2774	redis	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2775	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2776	celery	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2777	email	HEALTHY	\N	2026-08-19 18:14:44.167485
2778	backup	HEALTHY	\N	2026-08-19 18:14:44.167485
2779	sentry	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2780	openai	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2781	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:14:44.167485
2782	simulation	HEALTHY	\N	2026-08-19 18:14:44.167485
2783	application	HEALTHY	4.5	2026-08-19 18:14:44.167485
2784	database	HEALTHY	0.54	2026-08-19 18:15:14.21573
2785	redis	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2786	rabbitmq	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2787	celery	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2788	email	HEALTHY	\N	2026-08-19 18:15:14.21573
2789	backup	UNAVAILABLE	\N	2026-08-19 18:15:14.21573
2790	sentry	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2791	openai	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2792	cloudflare	NOT_CONFIGURED	\N	2026-08-19 18:15:14.21573
2793	simulation	HEALTHY	\N	2026-08-19 18:15:14.21573
2794	application	HEALTHY	4.5	2026-08-19 18:15:14.21573
\.


--
-- Data for Name: system_incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_incidents (id, category, severity, title, description, source, status, fingerprint, started_at, resolved_at, acknowledged_by, created_at) FROM stdin;
1	BACKUP	HIGH	Backups failing age / verification rules	Backup status: FAILED	health_check	OPEN	BACKUP_VERIFICATION_FAILED	2026-08-19 18:15:15.153466	\N	\N	2026-08-19 15:43:44.60599
\.


--
-- Data for Name: task_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_events (id, task_id, event_type, previous_status, new_status, user_id, created_at, reason, metadata) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, task_number, warehouse_id, task_type, priority, priority_score, status, source_type, source_id, order_id, order_item_id, product_id, source_location_id, destination_location_id, requested_quantity, completed_quantity, assigned_user_id, assigned_robot_id, created_at, prioritized_at, assigned_at, started_at, paused_at, completed_at, failed_at, cancelled_at, due_at, retry_count, failure_reason, notes, metadata, depends_on_task_id) FROM stdin;
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_sessions (id, user_id, session_token_hash, created_at, last_seen_at, expires_at, revoked_at, revoke_reason, login_method, ip_address, login_location, user_agent) FROM stdin;
\.


--
-- Data for Name: user_warehouse_access; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_warehouse_access (id, user_id, warehouse_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role, full_name, google_subject_id, created_at, updated_at, is_active, is_verified, last_login_at, last_logout_at, last_login_ip, login_location, login_method, failed_login_count, locked_until, email_verified_at, password_changed_at) FROM stdin;
2	test_admin	\N	$2b$12$YnltEE/2/PB4DM./KCArPOilz4NYQuH19u9DMAPBPfZ2r0r6TlmmO	admin		\N	2026-08-19 15:43:35.82341	2026-08-19 15:43:35.82341	t	f	\N	\N	\N	\N	\N	0	\N	\N	\N
3	test_manager	\N	$2b$12$GFo8sE.n54/fIADXyKInkucviTcgbabSwv8GzwGEvt397RMAB5bmO	manager		\N	2026-08-19 15:43:35.82341	2026-08-19 15:43:35.82341	t	f	\N	\N	\N	\N	\N	0	\N	\N	\N
4	test_viewer	\N	$2b$12$nQPG2Um5UqZfI6jK3B6.WetOxegfqLhd6Pce1RI9tUCKHBMph6XAy	viewer		\N	2026-08-19 15:43:35.82341	2026-08-19 15:44:20.675787	t	t	2026-08-19 15:44:20.667694	\N	127.0.0.1	\N	password	0	\N	\N	\N
6	harsha200797@gmail.com	harsha200797@gmail.com	GOOGLE_OAUTH_ONLY	admin	harshavardhan	\N	2026-08-19 16:55:59.998852	2026-08-19 16:55:59.998852	t	f	\N	\N	\N	\N	\N	0	\N	\N	\N
1	admin	\N	$2b$12$ZBDm0khkDRbz0JCeYWHKweMqEuIQNPH4U39P4IhVqCAKD5RILGQrK	admin	System Administrator	\N	2026-08-19 15:43:01.098298	2026-08-19 18:18:36.662353	t	t	2026-08-19 18:18:36.656975	\N	testclient	\N	password	0	\N	\N	\N
5	test_admin_hardened	\N	$2b$12$84cr.UVx0AzxuMsHIMGm7.rRHF2IndskJ7.2ytRfZF/BWKznDLGvq	admin		\N	2026-08-19 15:43:35.82341	2026-08-19 18:19:11.651927	t	t	2026-08-19 18:19:11.649912	\N	testclient	\N	password	0	\N	\N	\N
7	test_ai_manager	\N	$2b$12$0tyC9r9IQ.j2lN7BKKMMDOg2duwd4f4TKndygza/SK5G1RBTFX8Oq	manager		\N	2026-08-19 18:19:19.075792	2026-08-19 18:19:19.463199	t	t	2026-08-19 18:19:19.461182	\N	testclient	\N	password	0	\N	\N	\N
\.


--
-- Data for Name: warehouse_grid_cells; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_grid_cells (id, warehouse_id, x, y, cell_type, traversable, occupied, restricted, cost, metadata) FROM stdin;
\.


--
-- Data for Name: warehouse_locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_locations (id, warehouse_id, zone, aisle, rack, shelf, x, y, capacity, current_utilization, location_type, status, created_at) FROM stdin;
WH-WH-BLR-01-RECEIVING	WH-BLR-01	RECEIVING	1	1	1	1	5	500	0	RECEIVING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-SHIPPING	WH-BLR-01	SHIPPING	1	1	1	2	5	500	0	SHIPPING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-STAGING	WH-BLR-01	STAGING	1	1	1	6	5	500	0	STAGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-CHARGING-1	WH-BLR-01	CHARGING	1	1	1	11	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-CHARGING-2	WH-BLR-01	CHARGING	1	2	1	12	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CPU-01-STORAGE	WH-BLR-01	ZONE-A	1	01	1	2	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-GPU-01-STORAGE	WH-BLR-01	ZONE-A	1	01	1	3	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-RAM-01-STORAGE	WH-BLR-01	ZONE-A	1	01	1	4	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-SSD-01-STORAGE	WH-BLR-01	ZONE-B	1	01	1	6	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-HDD-01-STORAGE	WH-BLR-01	ZONE-B	1	01	1	7	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CHG-01-STORAGE	WH-BLR-01	ZONE-C	1	01	1	9	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CBL-01-STORAGE	WH-BLR-01	ZONE-C	1	01	1	10	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CPU-01-PICKING	WH-BLR-01	ZONE-A	1	01	1	2	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-GPU-01-PICKING	WH-BLR-01	ZONE-A	1	01	1	3	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-RAM-01-PICKING	WH-BLR-01	ZONE-A	1	01	1	4	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-SSD-01-PICKING	WH-BLR-01	ZONE-B	1	01	1	6	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-HDD-01-PICKING	WH-BLR-01	ZONE-B	1	01	1	7	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CHG-01-PICKING	WH-BLR-01	ZONE-C	1	01	1	9	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-LOC-ITM-CBL-01-PICKING	WH-BLR-01	ZONE-C	1	01	1	10	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-1-1	WH-BLR-01	AISLE	1	0	0	1	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-12-1	WH-BLR-01	AISLE	12	0	0	12	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-1-2	WH-BLR-01	AISLE	1	0	0	1	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-2-2	WH-BLR-01	AISLE	2	0	0	2	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-3-2	WH-BLR-01	AISLE	3	0	0	3	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-4-2	WH-BLR-01	AISLE	4	0	0	4	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-5-2	WH-BLR-01	AISLE	5	0	0	5	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-6-2	WH-BLR-01	AISLE	6	0	0	6	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-7-2	WH-BLR-01	AISLE	7	0	0	7	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-8-2	WH-BLR-01	AISLE	8	0	0	8	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-9-2	WH-BLR-01	AISLE	9	0	0	9	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-10-2	WH-BLR-01	AISLE	10	0	0	10	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-11-2	WH-BLR-01	AISLE	11	0	0	11	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-12-2	WH-BLR-01	AISLE	12	0	0	12	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-1-3	WH-BLR-01	AISLE	1	0	0	1	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-12-3	WH-BLR-01	AISLE	12	0	0	12	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-1-4	WH-BLR-01	AISLE	1	0	0	1	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-2-4	WH-BLR-01	AISLE	2	0	0	2	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-3-4	WH-BLR-01	AISLE	3	0	0	3	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-4-4	WH-BLR-01	AISLE	4	0	0	4	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-5-4	WH-BLR-01	AISLE	5	0	0	5	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-6-4	WH-BLR-01	AISLE	6	0	0	6	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-7-4	WH-BLR-01	AISLE	7	0	0	7	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-8-4	WH-BLR-01	AISLE	8	0	0	8	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-9-4	WH-BLR-01	AISLE	9	0	0	9	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-10-4	WH-BLR-01	AISLE	10	0	0	10	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-11-4	WH-BLR-01	AISLE	11	0	0	11	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-12-4	WH-BLR-01	AISLE	12	0	0	12	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-3-5	WH-BLR-01	AISLE	3	0	0	3	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-4-5	WH-BLR-01	AISLE	4	0	0	4	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-5-5	WH-BLR-01	AISLE	5	0	0	5	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-6-5	WH-BLR-01	AISLE	6	0	0	6	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-7-5	WH-BLR-01	AISLE	7	0	0	7	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-8-5	WH-BLR-01	AISLE	8	0	0	8	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-9-5	WH-BLR-01	AISLE	9	0	0	9	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BLR-01-AISLE-10-5	WH-BLR-01	AISLE	10	0	0	10	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-RECEIVING	WH-CHN-01	RECEIVING	1	1	1	1	5	500	0	RECEIVING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-SHIPPING	WH-CHN-01	SHIPPING	1	1	1	2	5	500	0	SHIPPING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-STAGING	WH-CHN-01	STAGING	1	1	1	6	5	500	0	STAGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-CHARGING-1	WH-CHN-01	CHARGING	1	1	1	11	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-CHARGING-2	WH-CHN-01	CHARGING	1	2	1	12	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CPU-01-STORAGE	WH-CHN-01	ZONE-A	1	01	1	2	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-GPU-01-STORAGE	WH-CHN-01	ZONE-A	1	01	1	3	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-RAM-01-STORAGE	WH-CHN-01	ZONE-A	1	01	1	4	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-SSD-01-STORAGE	WH-CHN-01	ZONE-B	1	01	1	6	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-HDD-01-STORAGE	WH-CHN-01	ZONE-B	1	01	1	7	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CHG-01-STORAGE	WH-CHN-01	ZONE-C	1	01	1	9	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CBL-01-STORAGE	WH-CHN-01	ZONE-C	1	01	1	10	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CPU-01-PICKING	WH-CHN-01	ZONE-A	1	01	1	2	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-GPU-01-PICKING	WH-CHN-01	ZONE-A	1	01	1	3	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-RAM-01-PICKING	WH-CHN-01	ZONE-A	1	01	1	4	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-SSD-01-PICKING	WH-CHN-01	ZONE-B	1	01	1	6	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-HDD-01-PICKING	WH-CHN-01	ZONE-B	1	01	1	7	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CHG-01-PICKING	WH-CHN-01	ZONE-C	1	01	1	9	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-LOC-ITM-CBL-01-PICKING	WH-CHN-01	ZONE-C	1	01	1	10	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-1-1	WH-CHN-01	AISLE	1	0	0	1	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-12-1	WH-CHN-01	AISLE	12	0	0	12	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-1-2	WH-CHN-01	AISLE	1	0	0	1	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-2-2	WH-CHN-01	AISLE	2	0	0	2	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-3-2	WH-CHN-01	AISLE	3	0	0	3	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-4-2	WH-CHN-01	AISLE	4	0	0	4	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-5-2	WH-CHN-01	AISLE	5	0	0	5	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-6-2	WH-CHN-01	AISLE	6	0	0	6	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-7-2	WH-CHN-01	AISLE	7	0	0	7	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-8-2	WH-CHN-01	AISLE	8	0	0	8	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-9-2	WH-CHN-01	AISLE	9	0	0	9	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-10-2	WH-CHN-01	AISLE	10	0	0	10	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-11-2	WH-CHN-01	AISLE	11	0	0	11	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-12-2	WH-CHN-01	AISLE	12	0	0	12	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-1-3	WH-CHN-01	AISLE	1	0	0	1	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-12-3	WH-CHN-01	AISLE	12	0	0	12	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-1-4	WH-CHN-01	AISLE	1	0	0	1	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-2-4	WH-CHN-01	AISLE	2	0	0	2	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-3-4	WH-CHN-01	AISLE	3	0	0	3	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-4-4	WH-CHN-01	AISLE	4	0	0	4	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-5-4	WH-CHN-01	AISLE	5	0	0	5	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-6-4	WH-CHN-01	AISLE	6	0	0	6	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-7-4	WH-CHN-01	AISLE	7	0	0	7	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-8-4	WH-CHN-01	AISLE	8	0	0	8	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-9-4	WH-CHN-01	AISLE	9	0	0	9	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-10-4	WH-CHN-01	AISLE	10	0	0	10	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-11-4	WH-CHN-01	AISLE	11	0	0	11	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-12-4	WH-CHN-01	AISLE	12	0	0	12	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-3-5	WH-CHN-01	AISLE	3	0	0	3	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-4-5	WH-CHN-01	AISLE	4	0	0	4	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-5-5	WH-CHN-01	AISLE	5	0	0	5	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-6-5	WH-CHN-01	AISLE	6	0	0	6	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-7-5	WH-CHN-01	AISLE	7	0	0	7	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-8-5	WH-CHN-01	AISLE	8	0	0	8	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-9-5	WH-CHN-01	AISLE	9	0	0	9	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-CHN-01-AISLE-10-5	WH-CHN-01	AISLE	10	0	0	10	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-RECEIVING	WH-BOM-01	RECEIVING	1	1	1	1	5	500	0	RECEIVING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-SHIPPING	WH-BOM-01	SHIPPING	1	1	1	2	5	500	0	SHIPPING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-STAGING	WH-BOM-01	STAGING	1	1	1	6	5	500	0	STAGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-CHARGING-1	WH-BOM-01	CHARGING	1	1	1	11	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-CHARGING-2	WH-BOM-01	CHARGING	1	2	1	12	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CPU-01-STORAGE	WH-BOM-01	ZONE-A	1	01	1	2	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-GPU-01-STORAGE	WH-BOM-01	ZONE-A	1	01	1	3	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-RAM-01-STORAGE	WH-BOM-01	ZONE-A	1	01	1	4	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-SSD-01-STORAGE	WH-BOM-01	ZONE-B	1	01	1	6	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-HDD-01-STORAGE	WH-BOM-01	ZONE-B	1	01	1	7	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CHG-01-STORAGE	WH-BOM-01	ZONE-C	1	01	1	9	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CBL-01-STORAGE	WH-BOM-01	ZONE-C	1	01	1	10	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CPU-01-PICKING	WH-BOM-01	ZONE-A	1	01	1	2	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-GPU-01-PICKING	WH-BOM-01	ZONE-A	1	01	1	3	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-RAM-01-PICKING	WH-BOM-01	ZONE-A	1	01	1	4	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-SSD-01-PICKING	WH-BOM-01	ZONE-B	1	01	1	6	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-HDD-01-PICKING	WH-BOM-01	ZONE-B	1	01	1	7	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CHG-01-PICKING	WH-BOM-01	ZONE-C	1	01	1	9	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-LOC-ITM-CBL-01-PICKING	WH-BOM-01	ZONE-C	1	01	1	10	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-1-1	WH-BOM-01	AISLE	1	0	0	1	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-12-1	WH-BOM-01	AISLE	12	0	0	12	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-1-2	WH-BOM-01	AISLE	1	0	0	1	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-2-2	WH-BOM-01	AISLE	2	0	0	2	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-3-2	WH-BOM-01	AISLE	3	0	0	3	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-4-2	WH-BOM-01	AISLE	4	0	0	4	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-5-2	WH-BOM-01	AISLE	5	0	0	5	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-6-2	WH-BOM-01	AISLE	6	0	0	6	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-7-2	WH-BOM-01	AISLE	7	0	0	7	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-8-2	WH-BOM-01	AISLE	8	0	0	8	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-9-2	WH-BOM-01	AISLE	9	0	0	9	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-10-2	WH-BOM-01	AISLE	10	0	0	10	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-11-2	WH-BOM-01	AISLE	11	0	0	11	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-12-2	WH-BOM-01	AISLE	12	0	0	12	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-1-3	WH-BOM-01	AISLE	1	0	0	1	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-12-3	WH-BOM-01	AISLE	12	0	0	12	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-1-4	WH-BOM-01	AISLE	1	0	0	1	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-2-4	WH-BOM-01	AISLE	2	0	0	2	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-3-4	WH-BOM-01	AISLE	3	0	0	3	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-4-4	WH-BOM-01	AISLE	4	0	0	4	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-5-4	WH-BOM-01	AISLE	5	0	0	5	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-6-4	WH-BOM-01	AISLE	6	0	0	6	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-7-4	WH-BOM-01	AISLE	7	0	0	7	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-8-4	WH-BOM-01	AISLE	8	0	0	8	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-9-4	WH-BOM-01	AISLE	9	0	0	9	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-10-4	WH-BOM-01	AISLE	10	0	0	10	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-11-4	WH-BOM-01	AISLE	11	0	0	11	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-12-4	WH-BOM-01	AISLE	12	0	0	12	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-3-5	WH-BOM-01	AISLE	3	0	0	3	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-4-5	WH-BOM-01	AISLE	4	0	0	4	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-5-5	WH-BOM-01	AISLE	5	0	0	5	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-6-5	WH-BOM-01	AISLE	6	0	0	6	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-7-5	WH-BOM-01	AISLE	7	0	0	7	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-8-5	WH-BOM-01	AISLE	8	0	0	8	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-9-5	WH-BOM-01	AISLE	9	0	0	9	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-BOM-01-AISLE-10-5	WH-BOM-01	AISLE	10	0	0	10	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-RECEIVING	WH-DEL-01	RECEIVING	1	1	1	1	5	500	0	RECEIVING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-SHIPPING	WH-DEL-01	SHIPPING	1	1	1	2	5	500	0	SHIPPING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-STAGING	WH-DEL-01	STAGING	1	1	1	6	5	500	0	STAGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-CHARGING-1	WH-DEL-01	CHARGING	1	1	1	11	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-CHARGING-2	WH-DEL-01	CHARGING	1	2	1	12	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-CPU-01-STORAGE	WH-DEL-01	ZONE-A	1	01	1	2	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-GPU-01-STORAGE	WH-DEL-01	ZONE-A	1	01	1	3	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-RAM-01-STORAGE	WH-DEL-01	ZONE-A	1	01	1	4	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-SSD-01-STORAGE	WH-DEL-01	ZONE-B	1	01	1	6	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-HDD-01-STORAGE	WH-DEL-01	ZONE-B	1	01	1	7	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-CHG-01-STORAGE	WH-DEL-01	ZONE-C	1	01	1	9	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-CBL-01-STORAGE	WH-DEL-01	ZONE-C	1	01	1	10	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.195432
WH-WH-DEL-01-LOC-ITM-CPU-01-PICKING	WH-DEL-01	ZONE-A	1	01	1	2	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-GPU-01-PICKING	WH-DEL-01	ZONE-A	1	01	1	3	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-RAM-01-PICKING	WH-DEL-01	ZONE-A	1	01	1	4	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-SSD-01-PICKING	WH-DEL-01	ZONE-B	1	01	1	6	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-HDD-01-PICKING	WH-DEL-01	ZONE-B	1	01	1	7	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-CHG-01-PICKING	WH-DEL-01	ZONE-C	1	01	1	9	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-LOC-ITM-CBL-01-PICKING	WH-DEL-01	ZONE-C	1	01	1	10	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-1-1	WH-DEL-01	AISLE	1	0	0	1	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-12-1	WH-DEL-01	AISLE	12	0	0	12	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-1-2	WH-DEL-01	AISLE	1	0	0	1	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-2-2	WH-DEL-01	AISLE	2	0	0	2	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-3-2	WH-DEL-01	AISLE	3	0	0	3	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-4-2	WH-DEL-01	AISLE	4	0	0	4	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-5-2	WH-DEL-01	AISLE	5	0	0	5	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-6-2	WH-DEL-01	AISLE	6	0	0	6	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-7-2	WH-DEL-01	AISLE	7	0	0	7	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-8-2	WH-DEL-01	AISLE	8	0	0	8	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-9-2	WH-DEL-01	AISLE	9	0	0	9	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-10-2	WH-DEL-01	AISLE	10	0	0	10	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-11-2	WH-DEL-01	AISLE	11	0	0	11	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-12-2	WH-DEL-01	AISLE	12	0	0	12	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-1-3	WH-DEL-01	AISLE	1	0	0	1	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-12-3	WH-DEL-01	AISLE	12	0	0	12	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-1-4	WH-DEL-01	AISLE	1	0	0	1	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-2-4	WH-DEL-01	AISLE	2	0	0	2	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-3-4	WH-DEL-01	AISLE	3	0	0	3	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-4-4	WH-DEL-01	AISLE	4	0	0	4	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-5-4	WH-DEL-01	AISLE	5	0	0	5	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-6-4	WH-DEL-01	AISLE	6	0	0	6	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-7-4	WH-DEL-01	AISLE	7	0	0	7	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-8-4	WH-DEL-01	AISLE	8	0	0	8	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-9-4	WH-DEL-01	AISLE	9	0	0	9	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-10-4	WH-DEL-01	AISLE	10	0	0	10	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-11-4	WH-DEL-01	AISLE	11	0	0	11	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-12-4	WH-DEL-01	AISLE	12	0	0	12	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-3-5	WH-DEL-01	AISLE	3	0	0	3	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-4-5	WH-DEL-01	AISLE	4	0	0	4	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-5-5	WH-DEL-01	AISLE	5	0	0	5	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-6-5	WH-DEL-01	AISLE	6	0	0	6	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-7-5	WH-DEL-01	AISLE	7	0	0	7	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-8-5	WH-DEL-01	AISLE	8	0	0	8	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-9-5	WH-DEL-01	AISLE	9	0	0	9	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-DEL-01-AISLE-10-5	WH-DEL-01	AISLE	10	0	0	10	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-RECEIVING	WH-CCU-01	RECEIVING	1	1	1	1	5	500	0	RECEIVING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-SHIPPING	WH-CCU-01	SHIPPING	1	1	1	2	5	500	0	SHIPPING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-STAGING	WH-CCU-01	STAGING	1	1	1	6	5	500	0	STAGING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-CHARGING-1	WH-CCU-01	CHARGING	1	1	1	11	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-CHARGING-2	WH-CCU-01	CHARGING	1	2	1	12	5	500	0	CHARGING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CPU-01-STORAGE	WH-CCU-01	ZONE-A	1	01	1	2	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-GPU-01-STORAGE	WH-CCU-01	ZONE-A	1	01	1	3	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-RAM-01-STORAGE	WH-CCU-01	ZONE-A	1	01	1	4	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-SSD-01-STORAGE	WH-CCU-01	ZONE-B	1	01	1	6	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-HDD-01-STORAGE	WH-CCU-01	ZONE-B	1	01	1	7	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CHG-01-STORAGE	WH-CCU-01	ZONE-C	1	01	1	9	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CBL-01-STORAGE	WH-CCU-01	ZONE-C	1	01	1	10	1	500	0	STORAGE	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CPU-01-PICKING	WH-CCU-01	ZONE-A	1	01	1	2	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-GPU-01-PICKING	WH-CCU-01	ZONE-A	1	01	1	3	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-RAM-01-PICKING	WH-CCU-01	ZONE-A	1	01	1	4	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-SSD-01-PICKING	WH-CCU-01	ZONE-B	1	01	1	6	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-HDD-01-PICKING	WH-CCU-01	ZONE-B	1	01	1	7	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CHG-01-PICKING	WH-CCU-01	ZONE-C	1	01	1	9	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-LOC-ITM-CBL-01-PICKING	WH-CCU-01	ZONE-C	1	01	1	10	3	500	0	PICKING	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-1-1	WH-CCU-01	AISLE	1	0	0	1	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-12-1	WH-CCU-01	AISLE	12	0	0	12	1	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-1-2	WH-CCU-01	AISLE	1	0	0	1	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-2-2	WH-CCU-01	AISLE	2	0	0	2	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-3-2	WH-CCU-01	AISLE	3	0	0	3	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-4-2	WH-CCU-01	AISLE	4	0	0	4	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-5-2	WH-CCU-01	AISLE	5	0	0	5	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-6-2	WH-CCU-01	AISLE	6	0	0	6	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-7-2	WH-CCU-01	AISLE	7	0	0	7	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-8-2	WH-CCU-01	AISLE	8	0	0	8	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-9-2	WH-CCU-01	AISLE	9	0	0	9	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-10-2	WH-CCU-01	AISLE	10	0	0	10	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-11-2	WH-CCU-01	AISLE	11	0	0	11	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-12-2	WH-CCU-01	AISLE	12	0	0	12	2	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-1-3	WH-CCU-01	AISLE	1	0	0	1	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-12-3	WH-CCU-01	AISLE	12	0	0	12	3	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-1-4	WH-CCU-01	AISLE	1	0	0	1	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-2-4	WH-CCU-01	AISLE	2	0	0	2	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-3-4	WH-CCU-01	AISLE	3	0	0	3	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-4-4	WH-CCU-01	AISLE	4	0	0	4	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-5-4	WH-CCU-01	AISLE	5	0	0	5	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-6-4	WH-CCU-01	AISLE	6	0	0	6	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-7-4	WH-CCU-01	AISLE	7	0	0	7	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-8-4	WH-CCU-01	AISLE	8	0	0	8	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-9-4	WH-CCU-01	AISLE	9	0	0	9	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-10-4	WH-CCU-01	AISLE	10	0	0	10	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-11-4	WH-CCU-01	AISLE	11	0	0	11	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-12-4	WH-CCU-01	AISLE	12	0	0	12	4	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-3-5	WH-CCU-01	AISLE	3	0	0	3	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-4-5	WH-CCU-01	AISLE	4	0	0	4	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-5-5	WH-CCU-01	AISLE	5	0	0	5	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-6-5	WH-CCU-01	AISLE	6	0	0	6	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-7-5	WH-CCU-01	AISLE	7	0	0	7	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-8-5	WH-CCU-01	AISLE	8	0	0	8	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-9-5	WH-CCU-01	AISLE	9	0	0	9	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
WH-WH-CCU-01-AISLE-10-5	WH-CCU-01	AISLE	10	0	0	10	5	500	0	BUFFER	ACTIVE	2026-08-19 18:18:37.19643
\.


--
-- Data for Name: warehouse_obstacles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouse_obstacles (id, warehouse_id, obstacle_type, x, y, width, height, active, severity, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.warehouses (id, name, location, latitude, longitude, created_at) FROM stdin;
WH-BLR-01	Bangalore Fulfillment Center	Bangalore, Karnataka	12.971598	77.594566	2026-08-19 18:18:37.157437
WH-CHN-01	Chennai Port Logistics Hub	Chennai, Tamil Nadu	13.08268	80.270718	2026-08-19 18:18:37.163434
WH-BOM-01	Mumbai Container Terminal	Mumbai, Maharashtra	19.07609	72.877701	2026-08-19 18:18:37.167435
WH-DEL-01	Delhi NCR Logistics Park	Noida, Uttar Pradesh	28.535517	77.391029	2026-08-19 18:18:37.172434
WH-CCU-01	Kolkata Gateway Depot	Kolkata, West Bengal	22.572646	88.363895	2026-08-19 18:18:37.175432
\.


--
-- Name: access_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.access_log_id_seq', 435, true);


--
-- Name: ai_recommendations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ai_recommendations_id_seq', 73, true);


--
-- Name: audit_ledger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_ledger_id_seq', 476, true);


--
-- Name: backup_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.backup_records_id_seq', 4, true);


--
-- Name: digital_twin_simulations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.digital_twin_simulations_id_seq', 1, true);


--
-- Name: experiment_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.experiment_runs_id_seq', 1, false);


--
-- Name: experiments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.experiments_id_seq', 2, true);


--
-- Name: health_thresholds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.health_thresholds_id_seq', 11, true);


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_id_seq', 280, true);


--
-- Name: inventory_reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_reservations_id_seq', 1, false);


--
-- Name: notification_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_preferences_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 49, true);


--
-- Name: order_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_events_id_seq', 1, false);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 1, false);


--
-- Name: otp_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.otp_records_id_seq', 1, true);


--
-- Name: packing_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.packing_records_id_seq', 1, false);


--
-- Name: recovery_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recovery_codes_id_seq', 1, false);


--
-- Name: recovery_credentials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recovery_credentials_id_seq', 1, false);


--
-- Name: robot_reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_reservations_id_seq', 1, false);


--
-- Name: robot_routes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_routes_id_seq', 1, false);


--
-- Name: robot_telemetry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robot_telemetry_id_seq', 6, true);


--
-- Name: robots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.robots_id_seq', 56, true);


--
-- Name: scenarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scenarios_id_seq', 2, true);


--
-- Name: shrinkage_flags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shrinkage_flags_id_seq', 16, true);


--
-- Name: simulation_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.simulation_events_id_seq', 1, true);


--
-- Name: simulation_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.simulation_snapshots_id_seq', 1, true);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_movements_id_seq', 8400, true);


--
-- Name: system_health_snapshots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_health_snapshots_id_seq', 2893, true);


--
-- Name: system_incidents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_incidents_id_seq', 5, true);


--
-- Name: task_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_events_id_seq', 2, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 2, true);


--
-- Name: user_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_sessions_id_seq', 1, false);


--
-- Name: user_warehouse_access_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_warehouse_access_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: warehouse_grid_cells_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_grid_cells_id_seq', 240, true);


--
-- Name: warehouse_obstacles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_obstacles_id_seq', 1, true);


--
-- Name: access_log access_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_log
    ADD CONSTRAINT access_log_pkey PRIMARY KEY (id);


--
-- Name: ai_recommendations ai_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_recommendations
    ADD CONSTRAINT ai_recommendations_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_ledger audit_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_ledger
    ADD CONSTRAINT audit_ledger_pkey PRIMARY KEY (id);


--
-- Name: backup_records backup_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_records
    ADD CONSTRAINT backup_records_pkey PRIMARY KEY (id);


--
-- Name: digital_twin_simulations digital_twin_simulations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations
    ADD CONSTRAINT digital_twin_simulations_pkey PRIMARY KEY (id);


--
-- Name: experiment_runs experiment_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs
    ADD CONSTRAINT experiment_runs_pkey PRIMARY KEY (id);


--
-- Name: experiments experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_pkey PRIMARY KEY (id);


--
-- Name: health_thresholds health_thresholds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_thresholds
    ADD CONSTRAINT health_thresholds_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: inventory_reservations inventory_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: notification_preferences notification_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: order_events order_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events
    ADD CONSTRAINT order_events_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: otp_records otp_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT otp_records_pkey PRIMARY KEY (id);


--
-- Name: packing_records packing_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records
    ADD CONSTRAINT packing_records_pkey PRIMARY KEY (id);


--
-- Name: recovery_codes recovery_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes
    ADD CONSTRAINT recovery_codes_pkey PRIMARY KEY (id);


--
-- Name: recovery_credentials recovery_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials
    ADD CONSTRAINT recovery_credentials_pkey PRIMARY KEY (id);


--
-- Name: robot_reservations robot_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_pkey PRIMARY KEY (id);


--
-- Name: robot_routes robot_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_pkey PRIMARY KEY (id);


--
-- Name: robot_telemetry robot_telemetry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry
    ADD CONSTRAINT robot_telemetry_pkey PRIMARY KEY (id);


--
-- Name: robots robots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_pkey PRIMARY KEY (id);


--
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (id);


--
-- Name: shrinkage_flags shrinkage_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shrinkage_flags
    ADD CONSTRAINT shrinkage_flags_pkey PRIMARY KEY (id);


--
-- Name: simulation_events simulation_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_pkey PRIMARY KEY (id);


--
-- Name: simulation_snapshots simulation_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: system_health_snapshots system_health_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health_snapshots
    ADD CONSTRAINT system_health_snapshots_pkey PRIMARY KEY (id);


--
-- Name: system_incidents system_incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_incidents
    ADD CONSTRAINT system_incidents_pkey PRIMARY KEY (id);


--
-- Name: task_events task_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: warehouse_grid_cells uq_grid_cell; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT uq_grid_cell UNIQUE (warehouse_id, x, y);


--
-- Name: stock_movements uq_movement; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT uq_movement UNIQUE (date, warehouse_id, item_id);


--
-- Name: otp_records uq_otp_user_purpose; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT uq_otp_user_purpose UNIQUE (user_id, purpose);


--
-- Name: notification_preferences uq_user_category_preference; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT uq_user_category_preference UNIQUE (user_id, category);


--
-- Name: user_warehouse_access uq_user_warehouse; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT uq_user_warehouse UNIQUE (user_id, warehouse_id);


--
-- Name: inventory uq_warehouse_item_location; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT uq_warehouse_item_location UNIQUE (warehouse_id, item_id, location_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_hash_key UNIQUE (session_token_hash);


--
-- Name: user_warehouse_access user_warehouse_access_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouse_grid_cells warehouse_grid_cells_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT warehouse_grid_cells_pkey PRIMARY KEY (id);


--
-- Name: warehouse_locations warehouse_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_pkey PRIMARY KEY (id);


--
-- Name: warehouse_obstacles warehouse_obstacles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles
    ADD CONSTRAINT warehouse_obstacles_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: ix_access_log_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_access_log_timestamp ON public.access_log USING btree ("timestamp");


--
-- Name: ix_ai_recommendations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_created_at ON public.ai_recommendations USING btree (created_at);


--
-- Name: ix_ai_recommendations_recommendation_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_recommendation_type ON public.ai_recommendations USING btree (recommendation_type);


--
-- Name: ix_ai_recommendations_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_recommendations_timestamp ON public.ai_recommendations USING btree ("timestamp");


--
-- Name: ix_backup_records_backup_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_backup_records_backup_id ON public.backup_records USING btree (backup_id);


--
-- Name: ix_backup_records_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_backup_records_created_at ON public.backup_records USING btree (created_at);


--
-- Name: ix_digital_twin_simulations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_created_at ON public.digital_twin_simulations USING btree (created_at);


--
-- Name: ix_digital_twin_simulations_simulation_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_simulation_status ON public.digital_twin_simulations USING btree (simulation_status);


--
-- Name: ix_digital_twin_simulations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_digital_twin_simulations_warehouse_id ON public.digital_twin_simulations USING btree (warehouse_id);


--
-- Name: ix_experiment_runs_experiment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_experiment_runs_experiment_id ON public.experiment_runs USING btree (experiment_id);


--
-- Name: ix_experiments_scenario_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_experiments_scenario_id ON public.experiments USING btree (scenario_id);


--
-- Name: ix_health_thresholds_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_health_thresholds_key ON public.health_thresholds USING btree (key);


--
-- Name: ix_inventory_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_item_id ON public.inventory USING btree (item_id);


--
-- Name: ix_inventory_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_location_id ON public.inventory USING btree (location_id);


--
-- Name: ix_inventory_reservations_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_created_at ON public.inventory_reservations USING btree (created_at);


--
-- Name: ix_inventory_reservations_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_item_id ON public.inventory_reservations USING btree (item_id);


--
-- Name: ix_inventory_reservations_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_location_id ON public.inventory_reservations USING btree (location_id);


--
-- Name: ix_inventory_reservations_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_reservations_order_id ON public.inventory_reservations USING btree (order_id);


--
-- Name: ix_inventory_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inventory_warehouse_id ON public.inventory USING btree (warehouse_id);


--
-- Name: ix_items_sku; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_items_sku ON public.items USING btree (sku);


--
-- Name: ix_notification_preferences_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_preferences_category ON public.notification_preferences USING btree (category);


--
-- Name: ix_notification_preferences_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_preferences_user_id ON public.notification_preferences USING btree (user_id);


--
-- Name: ix_notifications_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_created_at ON public.notifications USING btree (created_at);


--
-- Name: ix_notifications_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_event_type ON public.notifications USING btree (event_type);


--
-- Name: ix_notifications_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_status ON public.notifications USING btree (status);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_notifications_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_warehouse_id ON public.notifications USING btree (warehouse_id);


--
-- Name: ix_order_events_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_events_order_id ON public.order_events USING btree (order_id);


--
-- Name: ix_order_events_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_events_timestamp ON public.order_events USING btree ("timestamp");


--
-- Name: ix_order_items_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_item_id ON public.order_items USING btree (item_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_orders_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_created_at ON public.orders USING btree (created_at);


--
-- Name: ix_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_status ON public.orders USING btree (status);


--
-- Name: ix_orders_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_warehouse_id ON public.orders USING btree (warehouse_id);


--
-- Name: ix_otp_records_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_otp_records_expires_at ON public.otp_records USING btree (expires_at);


--
-- Name: ix_otp_records_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_otp_records_user_id ON public.otp_records USING btree (user_id);


--
-- Name: ix_packing_records_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_packing_records_order_id ON public.packing_records USING btree (order_id);


--
-- Name: ix_recovery_codes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recovery_codes_user_id ON public.recovery_codes USING btree (user_id);


--
-- Name: ix_recovery_credentials_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_recovery_credentials_user_id ON public.recovery_credentials USING btree (user_id);


--
-- Name: ix_robot_reservations_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_reservations_robot_id ON public.robot_reservations USING btree (robot_id);


--
-- Name: ix_robot_reservations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_reservations_warehouse_id ON public.robot_reservations USING btree (warehouse_id);


--
-- Name: ix_robot_routes_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_robot_id ON public.robot_routes USING btree (robot_id);


--
-- Name: ix_robot_routes_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_task_id ON public.robot_routes USING btree (task_id);


--
-- Name: ix_robot_routes_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_routes_warehouse_id ON public.robot_routes USING btree (warehouse_id);


--
-- Name: ix_robot_telemetry_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_telemetry_robot_id ON public.robot_telemetry USING btree (robot_id);


--
-- Name: ix_robot_telemetry_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robot_telemetry_timestamp ON public.robot_telemetry USING btree ("timestamp");


--
-- Name: ix_robots_assigned_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_assigned_task_id ON public.robots USING btree (assigned_task_id);


--
-- Name: ix_robots_current_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_current_location_id ON public.robots USING btree (current_location_id);


--
-- Name: ix_robots_robot_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_robots_robot_code ON public.robots USING btree (robot_code);


--
-- Name: ix_robots_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_status ON public.robots USING btree (status);


--
-- Name: ix_robots_target_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_target_location_id ON public.robots USING btree (target_location_id);


--
-- Name: ix_robots_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_robots_warehouse_id ON public.robots USING btree (warehouse_id);


--
-- Name: ix_scenarios_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scenarios_warehouse_id ON public.scenarios USING btree (warehouse_id);


--
-- Name: ix_shipments_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_shipments_order_id ON public.shipments USING btree (order_id);


--
-- Name: ix_simulation_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_event_type ON public.simulation_events USING btree (event_type);


--
-- Name: ix_simulation_events_real_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_real_timestamp ON public.simulation_events USING btree (real_timestamp);


--
-- Name: ix_simulation_events_robot_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_robot_id ON public.simulation_events USING btree (robot_id);


--
-- Name: ix_simulation_events_simulation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_simulation_id ON public.simulation_events USING btree (simulation_id);


--
-- Name: ix_simulation_events_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_task_id ON public.simulation_events USING btree (task_id);


--
-- Name: ix_simulation_events_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_events_warehouse_id ON public.simulation_events USING btree (warehouse_id);


--
-- Name: ix_simulation_snapshots_simulation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_snapshots_simulation_id ON public.simulation_snapshots USING btree (simulation_id);


--
-- Name: ix_simulation_snapshots_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_simulation_snapshots_warehouse_id ON public.simulation_snapshots USING btree (warehouse_id);


--
-- Name: ix_stock_movements_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_date ON public.stock_movements USING btree (date);


--
-- Name: ix_stock_movements_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_item_id ON public.stock_movements USING btree (item_id);


--
-- Name: ix_stock_movements_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_stock_movements_warehouse_id ON public.stock_movements USING btree (warehouse_id);


--
-- Name: ix_system_health_snapshots_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_health_snapshots_service ON public.system_health_snapshots USING btree (service);


--
-- Name: ix_system_health_snapshots_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_health_snapshots_timestamp ON public.system_health_snapshots USING btree ("timestamp");


--
-- Name: ix_system_incidents_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_incidents_category ON public.system_incidents USING btree (category);


--
-- Name: ix_system_incidents_fingerprint; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_incidents_fingerprint ON public.system_incidents USING btree (fingerprint);


--
-- Name: ix_task_events_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_task_events_task_id ON public.task_events USING btree (task_id);


--
-- Name: ix_tasks_assigned_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_assigned_user_id ON public.tasks USING btree (assigned_user_id);


--
-- Name: ix_tasks_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_created_at ON public.tasks USING btree (created_at);


--
-- Name: ix_tasks_destination_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_destination_location_id ON public.tasks USING btree (destination_location_id);


--
-- Name: ix_tasks_due_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_due_at ON public.tasks USING btree (due_at);


--
-- Name: ix_tasks_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_order_id ON public.tasks USING btree (order_id);


--
-- Name: ix_tasks_order_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_order_item_id ON public.tasks USING btree (order_item_id);


--
-- Name: ix_tasks_priority_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_priority_score ON public.tasks USING btree (priority_score);


--
-- Name: ix_tasks_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_product_id ON public.tasks USING btree (product_id);


--
-- Name: ix_tasks_source_location_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_source_location_id ON public.tasks USING btree (source_location_id);


--
-- Name: ix_tasks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_status ON public.tasks USING btree (status);


--
-- Name: ix_tasks_task_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tasks_task_number ON public.tasks USING btree (task_number);


--
-- Name: ix_tasks_task_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_task_type ON public.tasks USING btree (task_type);


--
-- Name: ix_tasks_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_warehouse_id ON public.tasks USING btree (warehouse_id);


--
-- Name: ix_user_sessions_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_expires_at ON public.user_sessions USING btree (expires_at);


--
-- Name: ix_user_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_sessions_user_id ON public.user_sessions USING btree (user_id);


--
-- Name: ix_user_warehouse_access_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_warehouse_access_user_id ON public.user_warehouse_access USING btree (user_id);


--
-- Name: ix_user_warehouse_access_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_warehouse_access_warehouse_id ON public.user_warehouse_access USING btree (warehouse_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_google_subject_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_google_subject_id ON public.users USING btree (google_subject_id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_warehouse_grid_cells_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_grid_cells_warehouse_id ON public.warehouse_grid_cells USING btree (warehouse_id);


--
-- Name: ix_warehouse_locations_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_locations_warehouse_id ON public.warehouse_locations USING btree (warehouse_id);


--
-- Name: ix_warehouse_obstacles_warehouse_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_warehouse_obstacles_warehouse_id ON public.warehouse_obstacles USING btree (warehouse_id);


--
-- Name: digital_twin_simulations digital_twin_simulations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_simulations
    ADD CONSTRAINT digital_twin_simulations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: experiment_runs experiment_runs_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_runs
    ADD CONSTRAINT experiment_runs_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE CASCADE;


--
-- Name: experiments experiments_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.scenarios(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_reservations inventory_reservations_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: inventory_reservations inventory_reservations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_reservations inventory_reservations_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_reservations
    ADD CONSTRAINT inventory_reservations_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: inventory inventory_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: notification_preferences notification_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_preferences
    ADD CONSTRAINT notification_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: order_events order_events_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_events
    ADD CONSTRAINT order_events_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: orders orders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: otp_records otp_records_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.otp_records
    ADD CONSTRAINT otp_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: packing_records packing_records_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.packing_records
    ADD CONSTRAINT packing_records_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: recovery_codes recovery_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_codes
    ADD CONSTRAINT recovery_codes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recovery_credentials recovery_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recovery_credentials
    ADD CONSTRAINT recovery_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: robot_reservations robot_reservations_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robot_reservations robot_reservations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_reservations
    ADD CONSTRAINT robot_reservations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: robot_routes robot_routes_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robot_routes robot_routes_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: robot_routes robot_routes_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_routes
    ADD CONSTRAINT robot_routes_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: robot_telemetry robot_telemetry_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robot_telemetry
    ADD CONSTRAINT robot_telemetry_robot_id_fkey FOREIGN KEY (robot_id) REFERENCES public.robots(id) ON DELETE CASCADE;


--
-- Name: robots robots_assigned_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_assigned_task_id_fkey FOREIGN KEY (assigned_task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: robots robots_current_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_current_location_id_fkey FOREIGN KEY (current_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: robots robots_target_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_target_location_id_fkey FOREIGN KEY (target_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: robots robots_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.robots
    ADD CONSTRAINT robots_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: scenarios scenarios_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: shipments shipments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: simulation_events simulation_events_simulation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_simulation_id_fkey FOREIGN KEY (simulation_id) REFERENCES public.digital_twin_simulations(id) ON DELETE CASCADE;


--
-- Name: simulation_events simulation_events_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_events
    ADD CONSTRAINT simulation_events_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: simulation_snapshots simulation_snapshots_simulation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_simulation_id_fkey FOREIGN KEY (simulation_id) REFERENCES public.digital_twin_simulations(id) ON DELETE CASCADE;


--
-- Name: simulation_snapshots simulation_snapshots_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_snapshots
    ADD CONSTRAINT simulation_snapshots_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: stock_movements stock_movements_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: stock_movements stock_movements_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: task_events task_events_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: task_events task_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_events
    ADD CONSTRAINT task_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_assigned_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_user_id_fkey FOREIGN KEY (assigned_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_depends_on_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_depends_on_task_id_fkey FOREIGN KEY (depends_on_task_id) REFERENCES public.tasks(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_destination_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_destination_location_id_fkey FOREIGN KEY (destination_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_order_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_order_item_id_fkey FOREIGN KEY (order_item_id) REFERENCES public.order_items(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: tasks tasks_source_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_source_location_id_fkey FOREIGN KEY (source_location_id) REFERENCES public.warehouse_locations(id) ON DELETE SET NULL;


--
-- Name: tasks tasks_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_warehouse_access user_warehouse_access_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_warehouse_access user_warehouse_access_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_warehouse_access
    ADD CONSTRAINT user_warehouse_access_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_grid_cells warehouse_grid_cells_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_grid_cells
    ADD CONSTRAINT warehouse_grid_cells_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_locations warehouse_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_locations
    ADD CONSTRAINT warehouse_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: warehouse_obstacles warehouse_obstacles_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse_obstacles
    ADD CONSTRAINT warehouse_obstacles_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict cMs6O96GyWgnOa90zUcKT3NKnlLkp44oeQdnQTPBIhX8qA8gWii3M09S4lgewYd

