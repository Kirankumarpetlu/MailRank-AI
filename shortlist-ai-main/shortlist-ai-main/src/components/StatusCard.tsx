import { motion } from "framer-motion";
import GlassCard from "./GlassCard";
import SparkleEffect from "./SparkleEffect";

type Status = "loading" | "selected" | "not_selected" | "error";

interface StatusCardProps {
  status: Status;
  company?: string;
  examDate?: string;
}

const LoadingState = () => (
  <div className="space-y-4">
    <div className="shimmer h-4 w-3/4 rounded-lg" />
    <div className="shimmer h-4 w-1/2 rounded-lg" />
    <div className="shimmer h-4 w-2/3 rounded-lg" />
    <p className="text-muted-foreground text-sm mt-6 animate-pulse">Checking your Gmail...</p>
  </div>
);

const SelectedState = ({ company, examDate }: { company: string; examDate: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <SparkleEffect />
    <div className="text-4xl mb-4">🎉</div>
    <h3 className="text-2xl font-bold text-foreground mb-2">Congratulations!</h3>
    <p className="text-success font-medium mb-4">You are shortlisted for {company}.</p>
    <div className="glass rounded-xl p-4 space-y-2 text-sm">
      <div className="flex justify-between">
        <span className="text-muted-foreground">Company</span>
        <span className="text-foreground font-medium">{company}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Exam Date</span>
        <span className="text-foreground font-medium">{examDate}</span>
      </div>
    </div>
  </motion.div>
);

const NotSelectedState = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="text-center py-4"
  >
    <p className="text-muted-foreground text-lg">No shortlist found today.</p>
  </motion.div>
);

const ErrorState = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="text-center py-4"
  >
    <p className="text-destructive text-lg font-medium">Something went wrong.</p>
    <p className="text-muted-foreground text-sm mt-1">Please try again.</p>
  </motion.div>
);

const variantMap: Record<Status, "default" | "success" | "muted" | "error"> = {
  loading: "default",
  selected: "success",
  not_selected: "muted",
  error: "error",
};

const StatusCard = ({ status, company, examDate }: StatusCardProps) => (
  <GlassCard
    variant={variantMap[status]}
    className="w-full max-w-lg relative"
    initial={{ opacity: 0, y: 20, scale: 0.97 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    key={status}
  >
    <h2 className="text-lg font-semibold text-foreground mb-5">Today's Shortlist Status</h2>
    {status === "loading" && <LoadingState />}
    {status === "selected" && (
      <SelectedState
        company={company || "Unknown Company"}
        examDate={examDate || "TBD"}
      />
    )}
    {status === "not_selected" && <NotSelectedState />}
    {status === "error" && <ErrorState />}
  </GlassCard>
);

export default StatusCard;
