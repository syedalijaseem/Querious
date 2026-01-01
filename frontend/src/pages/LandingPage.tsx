/**
 * LandingPage - Public landing page for Querious
 */
import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { pricingTiers } from "../constants/pricing";
import * as api from "../api";
import logo from "../assets/logo.png";
import {
  FileText,
  MessageSquare,
  BookOpen,
  FolderOpen,
  Shield,
  Zap,
  Menu,
  X,
  ArrowRight,
  Upload,
  HelpCircle,
  CheckCircle,
  Github,
  Linkedin,
  Sun,
  Moon,
  Mail,
} from "lucide-react";

// Feature data
const features = [
  {
    icon: FileText,
    title: "Smart Chunking",
    description: "Documents are intelligently split for accurate retrieval",
  },
  {
    icon: MessageSquare,
    title: "Natural Chat",
    description: "Ask questions in plain English, get clear answers",
  },
  {
    icon: BookOpen,
    title: "Source Citations",
    description: "Every answer includes page references you can verify",
  },
  {
    icon: FolderOpen,
    title: "Project Organization",
    description: "Group related documents into searchable projects",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your documents are encrypted and never shared",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Get answers in seconds, not minutes",
  },
];

// How it works steps
const steps = [
  {
    icon: Upload,
    title: "Upload",
    description: "Drop your PDFs into a chat or project",
  },
  {
    icon: HelpCircle,
    title: "Ask",
    description: "Type your question in natural language",
  },
  {
    icon: CheckCircle,
    title: "Get Answers",
    description: "Receive cited responses instantly",
  },
];

export function LandingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { actualTheme } = useTheme();
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  // For hero screenshot toggle - defaults to match system/app theme
  const [isDarkDemo, setIsDarkDemo] = useState(actualTheme === "dark");
  // Waitlist form state
  const [waitlistEmail, setWaitlistEmail] = useState("");
  const [waitlistStatus, setWaitlistStatus] = useState<
    "idle" | "loading" | "success" | "error" | "already"
  >("idle");
  const [waitlistMessage, setWaitlistMessage] = useState("");

  // Sync demo state with theme changes
  useEffect(() => {
    setIsDarkDemo(actualTheme === "dark");
  }, [actualTheme]);

  // Handle waitlist signup
  const handleWaitlistSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!waitlistEmail.trim()) return;

    setWaitlistStatus("loading");
    try {
      const result = await api.joinWaitlist(waitlistEmail);
      if (result.status === "already_registered") {
        setWaitlistStatus("already");
      } else {
        setWaitlistStatus("success");
      }
      setWaitlistMessage(result.message);
      setWaitlistEmail("");
      // Auto-hide after 5 seconds
      setTimeout(() => setWaitlistStatus("idle"), 5000);
    } catch {
      setWaitlistStatus("error");
      setWaitlistMessage("Something went wrong. Please try again.");
      setTimeout(() => setWaitlistStatus("idle"), 5000);
    }
  };

  // Track scroll for navbar blur
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Scroll-triggered animations
  const observerRef = useRef<IntersectionObserver | null>(null);
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll(".animate-on-scroll").forEach((el) => {
      observerRef.current?.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      {/* ========== NAVBAR ========== */}
      <nav
        className={`fixed top-0 w-full z-50 transition-all duration-300 ${
          isScrolled
            ? "bg-[var(--color-bg)]/80 backdrop-blur-md border-b border-[var(--color-border)]"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <img src={logo} alt="Querious" className="w-8 h-8" />
              <span className="text-xl font-bold text-[var(--color-text-primary)]">
                Querious
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-8">
              <button
                onClick={() => scrollToSection("features")}
                className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection("how-it-works")}
                className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              >
                How it Works
              </button>
              <button
                onClick={() => scrollToSection("pricing")}
                className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              >
                Pricing
              </button>
              {!user && (
                <Link
                  to="/login"
                  className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
                >
                  Log in
                </Link>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-[var(--color-text-secondary)]"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[var(--color-surface)] border-b border-[var(--color-border)]">
            <div className="px-4 py-4 space-y-3">
              <button
                onClick={() => scrollToSection("features")}
                className="block w-full text-left py-2 text-[var(--color-text-secondary)]"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection("how-it-works")}
                className="block w-full text-left py-2 text-[var(--color-text-secondary)]"
              >
                How it Works
              </button>
              <button
                onClick={() => scrollToSection("pricing")}
                className="block w-full text-left py-2 text-[var(--color-text-secondary)]"
              >
                Pricing
              </button>
              {!user && (
                <Link
                  to="/login"
                  className="block w-full text-left py-2 text-[var(--color-text-secondary)]"
                >
                  Log in
                </Link>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* ========== HERO SECTION ========== */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="animate-fade-up text-4xl sm:text-5xl lg:text-6xl font-bold text-[var(--color-text-primary)] leading-tight">
            Chat with your documents.
            <br />
            <span className="text-[var(--color-accent)]">
              Get answers instantly.
            </span>
          </h1>
          <p className="animate-fade-up animate-delay-200 mt-6 text-lg sm:text-xl text-[var(--color-text-secondary)] max-w-2xl mx-auto">
            Upload PDFs, ask questions in plain English, and get accurate
            answers with source citations.
          </p>
          <div className="animate-fade-up animate-delay-300 mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate(user ? "/home" : "/register")}
              className="btn-primary px-8 py-4 rounded-lg text-lg font-medium flex items-center justify-center gap-2"
            >
              {user ? "Go to Dashboard" : "Get Started Free"}
              <ArrowRight size={20} />
            </button>
            <button
              onClick={() => scrollToSection("how-it-works")}
              className="btn-secondary px-8 py-4 rounded-lg text-lg font-medium"
            >
              See how it works
            </button>
          </div>

          {/* Hero Screenshot with Theme Toggle */}
          <div className="animate-fade-up animate-delay-400 mt-16 relative max-w-4xl mx-auto">
            <div className="relative rounded-xl overflow-hidden shadow-2xl border border-[var(--color-border)]">
              {/* Dark mode screenshot */}
              <img
                src="/screenshots/hero_dark.png"
                alt="Querious chat interface - dark mode"
                className={`w-full transition-opacity duration-300 ${
                  isDarkDemo ? "opacity-100" : "opacity-0 absolute inset-0"
                }`}
              />
              {/* Light mode screenshot */}
              <img
                src="/screenshots/hero_light.png"
                alt="Querious chat interface - light mode"
                className={`w-full transition-opacity duration-300 ${
                  !isDarkDemo ? "opacity-100" : "opacity-0 absolute inset-0"
                }`}
              />
              {/* Theme toggle button */}
              <button
                onClick={() => setIsDarkDemo(!isDarkDemo)}
                className="absolute top-4 right-4 p-2.5 bg-[var(--color-surface)]/90 backdrop-blur-sm rounded-full border border-[var(--color-border)] shadow-lg hover:scale-110 transition-transform"
                title={
                  isDarkDemo ? "Switch to light mode" : "Switch to dark mode"
                }
              >
                {isDarkDemo ? (
                  <Sun size={18} className="text-amber-500" />
                ) : (
                  <Moon size={18} className="text-indigo-500" />
                )}
              </button>
            </div>
            {/* Subtle glow effect */}
            <div className="absolute -inset-4 bg-gradient-to-r from-[var(--color-accent)]/20 via-transparent to-[var(--color-accent)]/20 blur-3xl -z-10 opacity-50" />
          </div>
        </div>
      </section>

      {/* ========== FEATURES SECTION ========== */}
      <section id="features" className="py-20 px-4 bg-[var(--color-surface)]">
        <div className="max-w-6xl mx-auto">
          <h2 className="animate-on-scroll text-3xl sm:text-4xl font-bold text-center text-[var(--color-text-primary)] mb-16">
            Everything you need to work smarter
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="animate-on-scroll hover-scale p-6 rounded-xl bg-[var(--color-bg)] border border-[var(--color-border)]"
                style={{ transitionDelay: `${index * 0.1}s` }}
              >
                <feature.icon className="w-10 h-10 text-[var(--color-accent)] mb-4" />
                <h3 className="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
                  {feature.title}
                </h3>
                <p className="text-[var(--color-text-secondary)]">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== FEATURE SHOWCASE ========== */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto space-y-24">
          {/* Smart Search Feature */}
          <div className="animate-on-scroll grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1">
              <h3 className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] mb-4">
                Smart Vector Search
              </h3>
              <p className="text-lg text-[var(--color-text-secondary)] mb-6">
                Our AI finds the most relevant passages from your documents
                instantly. Watch as it searches through your content to surface
                exactly what you need.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Semantic understanding, not just keywords
                </li>
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Results ranked by relevance
                </li>
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Page references included
                </li>
              </ul>
            </div>
            <div className="order-1 lg:order-2">
              <div className="relative">
                <img
                  src={`/screenshots/search_${actualTheme}.png`}
                  alt="Smart search in action"
                  loading="lazy"
                  width={800}
                  height={500}
                  className="rounded-xl shadow-2xl border border-[var(--color-border)] transform rotate-1 hover:rotate-0 transition-transform duration-300"
                />
                <div className="absolute -inset-4 bg-gradient-to-r from-[var(--color-accent)]/10 to-transparent blur-2xl -z-10" />
              </div>
            </div>
          </div>

          {/* Projects Feature */}
          <div className="animate-on-scroll grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="relative">
                <img
                  src={`/screenshots/projects_${actualTheme}.png`}
                  alt="Organize with projects"
                  loading="lazy"
                  width={800}
                  height={500}
                  className="rounded-xl shadow-2xl border border-[var(--color-border)] transform -rotate-1 hover:rotate-0 transition-transform duration-300"
                />
                <div className="absolute -inset-4 bg-gradient-to-l from-[var(--color-accent)]/10 to-transparent blur-2xl -z-10" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] mb-4">
                Organize with Projects
              </h3>
              <p className="text-lg text-[var(--color-text-secondary)] mb-6">
                Group related documents into projects for focused research. Keep
                your work organized and easily searchable.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Create unlimited projects
                </li>
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Search within or across projects
                </li>
                <li className="flex items-center gap-3 text-[var(--color-text-secondary)]">
                  <CheckCircle
                    size={20}
                    className="text-[var(--color-accent)] flex-shrink-0"
                  />
                  Easy document management
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ========== HOW IT WORKS SECTION ========== */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="animate-on-scroll text-3xl sm:text-4xl font-bold text-center text-[var(--color-text-primary)] mb-16">
            How it works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div
                key={step.title}
                className="animate-on-scroll text-center"
                style={{ transitionDelay: `${index * 0.15}s` }}
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-accent-subtle)] flex items-center justify-center">
                  <step.icon className="w-8 h-8 text-[var(--color-accent)]" />
                </div>
                <div className="text-2xl font-bold text-[var(--color-accent)] mb-2">
                  {index + 1}
                </div>
                <h3 className="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
                  {step.title}
                </h3>
                <p className="text-[var(--color-text-secondary)]">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== PRICING SECTION ========== */}
      <section id="pricing" className="py-20 px-4 bg-[var(--color-surface)]">
        <div className="max-w-6xl mx-auto">
          <h2 className="animate-on-scroll text-3xl sm:text-4xl font-bold text-center text-[var(--color-text-primary)] mb-4">
            Simple Pricing
          </h2>
          <p className="animate-on-scroll text-center text-[var(--color-text-secondary)] mb-16">
            Start free, upgrade when you need
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingTiers.map((tier, index) => (
              <div
                key={tier.name}
                className={`animate-on-scroll hover-scale relative flex flex-col p-6 rounded-xl border transition-all ${
                  tier.highlighted
                    ? "border-amber-400 dark:border-amber-500 bg-gradient-to-b from-amber-50/50 to-transparent dark:from-amber-900/10"
                    : "border-[var(--color-border)] bg-[var(--color-bg)]"
                }`}
                style={{ transitionDelay: `${index * 0.1}s` }}
              >
                {tier.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-semibold rounded-full">
                    ⭐ {tier.badge}
                  </div>
                )}
                <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
                  {tier.name}
                </h3>
                <div className="mb-4">
                  <span className="text-3xl font-bold text-[var(--color-text-primary)]">
                    {tier.price}
                  </span>
                  <span className="text-[var(--color-text-secondary)] text-sm">
                    {tier.period}
                  </span>
                </div>
                <ul className="flex-1 space-y-2 mb-6">
                  {tier.features.map((feature) => (
                    <li
                      key={feature.text}
                      className="flex items-start gap-2 text-sm text-[var(--color-text-secondary)]"
                    >
                      <span className="text-[var(--color-accent)]">✓</span>
                      {feature.text}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => !tier.comingSoon && navigate("/register")}
                  disabled={tier.comingSoon}
                  className={`w-full py-3 px-4 rounded-lg font-medium text-sm transition-all ${
                    tier.comingSoon
                      ? "bg-[var(--color-border)] text-[var(--color-text-tertiary)] cursor-not-allowed"
                      : tier.highlighted
                      ? "bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                      : "btn-primary"
                  }`}
                >
                  {tier.comingSoon ? "Coming Soon" : "Get Started"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== WAITLIST SECTION ========== */}
      {!user && (
        <section className="py-20 px-4">
          <div className="max-w-3xl mx-auto">
            <div className="relative p-8 sm:p-12 rounded-2xl bg-gradient-to-br from-[var(--color-surface)] to-[var(--color-bg)] border border-[var(--color-border)] overflow-hidden">
              {/* Decorative gradient blur */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[var(--color-accent)]/20 to-transparent blur-3xl -z-10" />
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-[var(--color-accent)]/10 to-transparent blur-3xl -z-10" />

              <div className="text-center mb-8">
                <h2 className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] mb-3">
                  Be the first to know
                </h2>
                <p className="text-[var(--color-text-secondary)]">
                  Get notified when Pro & Premium plans launch
                </p>
              </div>

              <form
                onSubmit={handleWaitlistSubmit}
                className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
              >
                <div className="relative flex-1">
                  <Mail
                    size={18}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
                  />
                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={waitlistEmail}
                    onChange={(e) => setWaitlistEmail(e.target.value)}
                    className="w-full pl-11 pr-4 py-3.5 rounded-xl bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-all"
                    disabled={waitlistStatus === "loading"}
                  />
                </div>
                <button
                  type="submit"
                  disabled={
                    waitlistStatus === "loading" || !waitlistEmail.trim()
                  }
                  className="px-8 py-3.5 rounded-xl bg-[var(--color-accent)] text-white font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all whitespace-nowrap shadow-lg shadow-[var(--color-accent)]/25"
                >
                  {waitlistStatus === "loading"
                    ? "Joining..."
                    : "Join Waitlist"}
                </button>
              </form>

              {/* Status Alert */}
              {waitlistStatus !== "idle" && waitlistStatus !== "loading" && (
                <div
                  className={`mt-6 mx-auto max-w-md px-4 py-3 rounded-xl text-sm font-medium text-center animate-fade-up ${
                    waitlistStatus === "success"
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : waitlistStatus === "already"
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "bg-red-500/10 text-red-400 border border-red-500/20"
                  }`}
                >
                  {waitlistMessage}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ========== FOOTER ========== */}
      <footer className="border-t border-[var(--color-border)]">
        {/* Main footer content */}
        <div className="py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex items-center gap-2">
                <img src={logo} alt="Querious" className="w-6 h-6" />
                <span className="text-lg font-bold text-[var(--color-text-primary)]">
                  Querious
                </span>
              </div>
              <div className="flex gap-6 text-sm text-[var(--color-text-secondary)]">
                <button
                  onClick={() => scrollToSection("features")}
                  className="hover:text-[var(--color-text-primary)] transition-colors"
                >
                  Features
                </button>
                <button
                  onClick={() => scrollToSection("pricing")}
                  className="hover:text-[var(--color-text-primary)] transition-colors"
                >
                  Pricing
                </button>
                <a
                  href="mailto:support@querious.dev"
                  className="hover:text-[var(--color-text-primary)] transition-colors"
                >
                  Contact
                </a>
              </div>
              <p className="text-sm text-[var(--color-text-tertiary)]">
                © 2025 Querious. All rights reserved.
              </p>
            </div>
          </div>
        </div>

        {/* Built by line */}
        <div className="py-3 px-4 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface)]">
          <div className="max-w-6xl mx-auto flex items-center justify-center gap-3 text-xs text-[var(--color-text-tertiary)]">
            <span>Built by</span>
            <span className="font-medium text-[var(--color-text-secondary)]">
              Syed Ali Jaseem
            </span>
            <span className="text-[var(--color-border)]">·</span>
            <a
              href="https://github.com/syedalijaseem"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[var(--color-text-primary)] transition-colors"
            >
              <Github size={14} />
            </a>
            <a
              href="https://linkedin.com/in/syedalijaseem"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[var(--color-text-primary)] transition-colors"
            >
              <Linkedin size={14} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
