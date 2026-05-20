-- complain if script is sourced in psql, rather than via CREATE EXTENSION
\echo Use "ALTER EXTENSION vector UPDATE TO '0.7.1'" to load this file. \quit

CREATE TABLE IF NOT EXISTS exqutor_qerror (
    table_name TEXT,
    column_name TEXT,
    sample_size FLOAT,
    recent_qerrors FLOAT[],
    qerror_count INT,
    v_grad FLOAT,
    learning_rate FLOAT,
    PRIMARY KEY (table_name, column_name)
);