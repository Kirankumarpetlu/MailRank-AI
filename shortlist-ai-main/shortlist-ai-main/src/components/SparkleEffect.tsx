import { motion } from "framer-motion";

const sparkles = Array.from({ length: 12 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 4 + 2,
  delay: Math.random() * 3,
  duration: Math.random() * 2 + 1.5,
}));

const SparkleEffect = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {sparkles.map((s) => (
      <motion.div
        key={s.id}
        className="absolute rounded-full bg-success"
        style={{
          width: s.size,
          height: s.size,
          left: `${s.x}%`,
          top: `${s.y}%`,
        }}
        animate={{
          opacity: [0, 1, 0],
          scale: [0, 1.2, 0],
        }}
        transition={{
          duration: s.duration,
          delay: s.delay,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    ))}
  </div>
);

export default SparkleEffect;
