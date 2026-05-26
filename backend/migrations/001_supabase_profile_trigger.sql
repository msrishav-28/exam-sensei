-- ExamSensei: Supabase auth.users → public.users sync
--
-- Run this ONCE in the Supabase SQL Editor after the application has created
-- the `users` table (it will be created automatically on first boot by
-- SQLAlchemy's `create_tables()`).
--
-- Effect: every time a new user signs up via the Supabase Auth SDK, this
-- trigger copies their id + metadata into the application's `public.users`
-- table so the FastAPI backend always has a matching row to query.
--
-- The frontend should call supabase.auth.signUp with `options.data` containing
-- the registration form fields, e.g.:
--   supabase.auth.signUp({
--     email, password,
--     options: { data: { name, education_level, state, category, budget } }
--   })

CREATE OR REPLACE FUNCTION public.handle_new_supabase_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.users (
        id, email, name, education_level, state, category, budget,
        current_stage, is_active, is_verified, created_at, updated_at
    ) VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'education_level', 'class_12'),
        COALESCE(NEW.raw_user_meta_data->>'state', ''),
        COALESCE(NEW.raw_user_meta_data->>'category', 'general'),
        COALESCE(NEW.raw_user_meta_data->>'budget', 'medium'),
        'class_12',
        TRUE,
        COALESCE(NEW.email_confirmed_at IS NOT NULL, FALSE),
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;  -- idempotent: trigger may fire on resend
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_supabase_user();

-- Optional: also sync email verification status when the user confirms email.
CREATE OR REPLACE FUNCTION public.handle_supabase_user_updated()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    UPDATE public.users
       SET email = NEW.email,
           is_verified = COALESCE(NEW.email_confirmed_at IS NOT NULL, FALSE),
           updated_at = NOW()
     WHERE id = NEW.id;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;

CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE ON auth.users
    FOR EACH ROW
    WHEN (OLD.email IS DISTINCT FROM NEW.email
       OR OLD.email_confirmed_at IS DISTINCT FROM NEW.email_confirmed_at)
    EXECUTE FUNCTION public.handle_supabase_user_updated();
