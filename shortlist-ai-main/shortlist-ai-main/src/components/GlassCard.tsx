import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { forwardRef, type ReactNode } from "react";

interface GlassCardProps {
  variant?: "default" | "strong" | "success" | "error" | "muted";
  hover?: boolean;
  className?: string;
  children?: ReactNode;
  initial?: any;
  animate?: any;
  transition?: any;
  exit?: any;
  [key: string]: any;
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = "default", hover = false, children, ...props }, ref) => {
    const variantClasses = {
      default: "glass",
      strong: "glass-strong",
      success: "glass glow-success",
      error: "glass glow-error",
      muted: "glass glow-muted",
    };

    return (
      <motion.div
        ref={ref}
        className={cn(
          variantClasses[variant],
          "rounded-2xl p-6 md:p-8",
          hover && "transition-transform duration-300 hover:scale-[1.02]",
          className
        )}
        {...props}
      >
        {/* Highlight edge */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-foreground/10 to-transparent" />
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = "GlassCard";
export default GlassCard;
