"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useAppStore } from "@/store/app-store";
import { Logo, Wordmark } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormValues = z.infer<typeof schema>;

export function LoginView() {
  const { login } = useAuth();
  const navigate = useAppStore((s) => s.navigate);
  const [showPw, setShowPw] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    setSubmitting(true);
    try {
      await login(values.email, values.password);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <div className="flex-1 flex flex-col justify-center px-6 py-10 max-w-md mx-auto w-full">
        <div className="mb-8 flex flex-col items-center text-center pp-animate-in">
          <Logo size={56} />
          <Wordmark className="text-2xl mt-3" />
        </div>

        <div className="bg-porcelain rounded-2xl border border-border/60 shadow-sm p-6 pp-animate-in">
          <h1 className="text-xl font-semibold text-graphite">Sign in</h1>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-5">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-graphite/40" />
                <Input
                  id="email"
                  className="pl-9"
                  placeholder="e.g. owner@example.com"
                  autoComplete="email"
                  {...register("email")}
                />
              </div>
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-graphite/40" />
                <Input
                  id="password"
                  type={showPw ? "text" : "password"}
                  className="pl-9 pr-9"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  {...register("password")}
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-graphite/40 hover:text-graphite/70"
                >
                  {showPw ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full bg-jungle-teal hover:bg-jungle-teal/90 text-white h-11"
              disabled={submitting}
            >
              {submitting ? "Signing in…" : "Sign in"}
              {!submitting && <ArrowRight className="size-4" />}
            </Button>
          </form>

          <p className="text-sm text-center text-graphite/60 mt-6">
            New to PagarPal?{" "}
            <button
              onClick={() => navigate("register")}
              className="text-jungle-teal font-medium hover:underline"
            >
              Create an account
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
