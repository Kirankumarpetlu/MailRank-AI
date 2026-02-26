import { motion } from "framer-motion";

const shapes = [
  { size: 400, x: "10%", y: "20%", color: "var(--gradient-purple)", delay: 0, duration: 12 },
  { size: 350, x: "70%", y: "60%", color: "var(--gradient-blue)", delay: 2, duration: 15 },
  { size: 250, x: "50%", y: "10%", color: "var(--gradient-cyan)", delay: 4, duration: 10 },
  { size: 300, x: "80%", y: "20%", color: "var(--gradient-purple)", delay: 1, duration: 13 },
  { size: 200, x: "20%", y: "70%", color: "var(--gradient-blue)", delay: 3, duration: 11 },
];

const AnimatedBackground = () => (
  <div className="fixed inset-0 overflow-hidden -z-10">
    {/* Base gradient */}
    <div
      className="absolute inset-0 animate-gradient-shift"
      style={{
        background: `linear-gradient(135deg, 
          hsl(260, 40%, 8%) 0%, 
          hsl(230, 35%, 10%) 30%, 
          hsl(220, 45%, 8%) 60%, 
          hsl(250, 35%, 10%) 100%)`,
        backgroundSize: "400% 400%",
      }}
    />

    {/* Floating gradient shapes */}
    {shapes.map((shape, i) => (
      <motion.div
        key={i}
        className="absolute rounded-full"
        style={{
          width: shape.size,
          height: shape.size,
          left: shape.x,
          top: shape.y,
          background: `radial-gradient(circle, hsla(${shape.color} / 0.15) 0%, transparent 70%)`,
          filter: "blur(60px)",
        }}
        animate={{
          y: [0, -30, 20, -10, 0],
          x: [0, 15, -10, 5, 0],
          scale: [1, 1.1, 0.95, 1.05, 1],
        }}
        transition={{
          duration: shape.duration,
          delay: shape.delay,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    ))}

    {/* Noise overlay */}
    <div className="noise-overlay" />
  </div>
);

export default AnimatedBackground;
