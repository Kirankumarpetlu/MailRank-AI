import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import AnimatedBackground from "@/components/AnimatedBackground";
import Navbar from "@/components/Navbar";
import StatusCard from "@/components/StatusCard";
import { useAuth } from "@/hooks/useAuth";

type Status = "loading" | "selected" | "not_selected" | "error";

interface ShortlistData {
    company?: string;
    examDate?: string;
}

const Dashboard = () => {
    const { token, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();
    const [status, setStatus] = useState<Status>("loading");
    const [data, setData] = useState<ShortlistData>({});

    // Guard: redirect to landing if not authenticated
    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/", { replace: true });
        }
    }, [isAuthenticated, navigate]);

    // Fetch shortlist status from API
    useEffect(() => {
        if (!token) return;

        const controller = new AbortController();

        const checkShortlist = async () => {
            setStatus("loading");
            try {
                const res = await fetch("http://localhost:8000/check-shortlist", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                    signal: controller.signal,
                });

                if (res.status === 401) {
                    // Token expired or invalid
                    logout();
                    return;
                }

                if (!res.ok) {
                    setStatus("error");
                    return;
                }

                const result = await res.json();

                if (result.shortlisted) {
                    setData({
                        company: result.company || "Unknown Company",
                        examDate: result.exam_date || "TBD",
                    });
                    setStatus("selected");
                } else {
                    setStatus("not_selected");
                }
            } catch (err: any) {
                if (err.name !== "AbortError") {
                    setStatus("error");
                }
            }
        };

        checkShortlist();

        return () => controller.abort();
    }, [token, logout]);

    if (!isAuthenticated) return null;

    return (
        <div className="min-h-screen relative">
            <AnimatedBackground />

            <motion.div
                className="min-h-screen pt-20"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.4 }}
            >
                <Navbar userName="User" onLogout={logout} />

                <div className="flex flex-col items-center justify-center min-h-[calc(100vh-5rem)] p-4 gap-6">
                    <AnimatePresence mode="wait">
                        <StatusCard
                            status={status}
                            company={data.company}
                            examDate={data.examDate}
                            key={status}
                        />
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
};

export default Dashboard;
