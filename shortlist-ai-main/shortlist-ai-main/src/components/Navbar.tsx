import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { LogOut, User, ChevronDown } from "lucide-react";

interface NavbarProps {
  userName: string;
  onLogout: () => void;
}

const Navbar = ({ userName, onLogout }: NavbarProps) => {
  const [open, setOpen] = useState(false);

  return (
    <motion.nav
      className="fixed top-0 inset-x-0 z-50 glass-strong"
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
        <span className="text-lg font-bold tracking-tight text-foreground">
          Shortlist AI
        </span>

        <div className="relative">
          <button
            onClick={() => setOpen(!open)}
            className="flex items-center gap-2 glass rounded-full px-4 py-2 text-sm font-medium text-foreground transition-all hover:scale-105"
          >
            <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="w-4 h-4 text-primary" />
            </div>
            <span className="hidden sm:inline">{userName}</span>
            <ChevronDown className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {open && (
              <motion.div
                className="absolute right-0 mt-2 w-48 glass-strong rounded-xl overflow-hidden"
                initial={{ opacity: 0, y: -8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
              >
                <button
                  onClick={onLogout}
                  className="flex items-center gap-3 w-full px-4 py-3 text-sm text-foreground transition-colors hover:bg-foreground/5"
                >
                  <LogOut className="w-4 h-4 text-muted-foreground" />
                  Sign out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
