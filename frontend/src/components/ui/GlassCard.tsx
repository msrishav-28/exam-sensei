import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
    hoverEffect?: boolean;
}

export function GlassCard({ children, className, hoverEffect = true, ...props }: GlassCardProps) {
    return (
        <div
            className={cn(
                "glass rounded-2xl p-6 transition-all duration-300",
                hoverEffect && "hover:bg-white/10 hover:scale-[1.01] hover:shadow-2xl hover:shadow-primary/10",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
