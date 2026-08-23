CREATE TYPE statusenum AS ENUM ('Not Applied', 'Applied', 'Interviewing', 'Offer Accepted', 'Application Archived')

CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "username" varchar,
  "email" varchar,
  "password" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "jobs" (
  "id" SERIAL PRIMARY KEY,
  "job_title" varchar,
  "company" varchar,
  "source" text,
  "description" text,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "user_jobs" (
  "id" SERIAL PRIMARY KEY,
  "user_id" integer REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE,
  "job_id" integer REFERENCES "jobs" ("id") DEFERRABLE INITIALLY IMMEDIATE,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "application_status" statusenum DEFAULT 'Not Applied',
  "is_archived" bool DEFAULT false
);