/**
 * Settings page component with Tailwind CSS - includes theme toggle.
 */
import { useState, useEffect, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import * as api from "../api";
import type { Session } from "../types";
import { LoadingSpinner } from "../components/LoadingSpinner";

interface SettingsPageProps {
  onClose: () => void;
}

export function SettingsPage({ onClose }: SettingsPageProps) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<
    "profile" | "appearance" | "security" | "sessions" | "danger"
  >("profile");

  return (
    <div className="min-h-screen w-full bg-neutral-100 dark:bg-[#242424] transition-colors">
      {/* Header - matches sidebar h-14 md:h-16 */}
      <div className="h-14 md:h-16 border-b border-[#e8e8e8] dark:border-[#3a3a3a] bg-[#f8f8f8] dark:bg-[#242424]">
        <div className="h-full max-w-4xl mx-auto px-6 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-[#1a1a1a] dark:text-[#ececec]">
            Settings
          </h1>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-[#a3a3a3] hover:text-[#1a1a1a] hover:bg-neutral-100 dark:hover:text-white dark:hover:bg-neutral-800 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-1 mb-8 p-1 bg-neutral-200/50 dark:bg-[#242424]/50 rounded-xl w-fit">
          {[
            { id: "profile", label: "Profile" },
            { id: "appearance", label: "Appearance" },
            // { id: "security", label: "Security" }, // Coming soon
            { id: "sessions", label: "Sessions" },
            { id: "danger", label: "Privacy" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? (tab as { danger?: boolean }).danger
                    ? "bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 shadow-sm"
                    : "bg-[#e6f7f5] dark:bg-[#0f2e2b] text-[#0f766e] dark:text-[#2dd4bf] shadow-sm"
                  : (tab as { danger?: boolean }).danger
                  ? "text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10"
                  : "text-zinc-600 dark:text-[#737373] hover:text-[#1a1a1a] dark:hover:text-white hover:bg-[#f0f0f0] dark:hover:bg-[#2a2a2a]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-[#f8f8f8] dark:bg-[#242424] rounded-2xl border border-[#e8e8e8] dark:border-[#3a3a3a] p-6">
          {activeTab === "profile" && <ProfileTab user={user} />}
          {activeTab === "appearance" && <AppearanceTab />}
          {/* {activeTab === "security" && <SecurityTab onLogout={logout} />} */}
          {activeTab === "sessions" && <SessionsTab />}
          {activeTab === "danger" && <DangerTab />}
        </div>
      </div>
    </div>
  );
}

// --- Profile Tab ---
function ProfileTab({
  user,
}: {
  user: { name?: string; email?: string } | null;
}) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#ececec] mb-6">
        Profile Information
      </h2>

      {/* Email - read only */}
      <div className="max-w-md">
        <label className="block text-sm font-medium text-neutral-700 dark:text-zinc-300 mb-1.5">
          Email
        </label>
        <input
          type="email"
          value={user?.email || ""}
          disabled
          className="w-full px-4 py-3 rounded-xl border border-[#e8e8e8] dark:border-[#3a3a3a] 
                     bg-neutral-100 dark:bg-[#242424] text-[#a3a3a3] dark:text-[#a0a0a0]
                     cursor-not-allowed"
        />
        <p className="mt-1.5 text-xs text-[#a3a3a3]">
          Contact support to update your account details
        </p>
      </div>
    </div>
  );
}

// --- Appearance Tab ---
function AppearanceTab() {
  const { theme, setTheme } = useTheme();

  const themes = [
    { id: "light", label: "Light", icon: "☀️" },
    { id: "dark", label: "Dark", icon: "🌙" },
    { id: "system", label: "System", icon: "💻" },
  ] as const;

  return (
    <div>
      <h2 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#ececec] mb-2">
        Appearance
      </h2>
      <p className="text-sm text-[#a3a3a3] dark:text-[#a0a0a0] mb-6">
        Choose how Querious looks on your device
      </p>

      <div className="flex gap-4">
        {themes.map((t) => (
          <button
            key={t.id}
            onClick={() => setTheme(t.id)}
            className={`flex-1 max-w-[160px] p-4 rounded-xl border-2 transition-all ${
              theme === t.id
                ? "border-orange-500 bg-orange-50 dark:bg-orange-900/20"
                : "border-[#e8e8e8] dark:border-[#3a3a3a] hover:border-zinc-300 dark:hover:border-zinc-600"
            }`}
          >
            <div className="text-2xl mb-2">{t.icon}</div>
            <div
              className={`text-sm font-medium ${
                theme === t.id
                  ? "text-[#0f766e] dark:text-[#2dd4bf]"
                  : "text-neutral-700 dark:text-zinc-300"
              }`}
            >
              {t.label}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

// --- Security Tab (Coming Soon) ---
export function SecurityTab({ onLogout }: { onLogout: () => void }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  async function handleChangePassword(e: FormEvent) {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setMessage({ type: "error", text: "Passwords do not match" });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      await api.changePassword(currentPassword, newPassword);
      setMessage({ type: "success", text: "Password changed successfully" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to change password",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleLogoutAll() {
    try {
      await api.logoutAll();
      onLogout();
    } catch (err) {
      setMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Failed to logout",
      });
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#ececec] mb-6">
        Change Password
      </h2>

      {message && (
        <div
          className={`mb-6 px-4 py-3 rounded-lg text-sm ${
            message.type === "success"
              ? "bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800"
              : "bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800"
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-zinc-300 mb-1.5">
            Current password
          </label>
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-xl border border-zinc-300 dark:border-[#3a3a3a] 
                       bg-[#f8f8f8] dark:bg-[#242424] text-[#1a1a1a] dark:text-[#ececec]
                       focus:ring-2 focus:ring-[#0d9488] focus:border-transparent
                       transition-all outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-zinc-300 mb-1.5">
            New password
          </label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-xl border border-zinc-300 dark:border-[#3a3a3a] 
                       bg-[#f8f8f8] dark:bg-[#242424] text-[#1a1a1a] dark:text-[#ececec]
                       focus:ring-2 focus:ring-[#0d9488] focus:border-transparent
                       transition-all outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-zinc-300 mb-1.5">
            Confirm new password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="w-full px-4 py-3 rounded-xl border border-zinc-300 dark:border-[#3a3a3a] 
                       bg-[#f8f8f8] dark:bg-[#242424] text-[#1a1a1a] dark:text-[#ececec]
                       focus:ring-2 focus:ring-[#0d9488] focus:border-transparent
                       transition-all outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl font-medium text-sm
                     bg-neutral-800 dark:bg-[#f8f8f8] text-white dark:text-[#1a1a1a]
                     hover:bg-neutral-800 dark:hover:bg-neutral-100
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all"
        >
          {loading ? "Changing..." : "Change password"}
        </button>
      </form>

      {/* Danger Zone */}
      <div className="mt-12 pt-8 border-t border-[#e8e8e8] dark:border-[#3a3a3a]">
        <h3 className="text-sm font-medium text-red-600 dark:text-red-400 mb-4">
          Danger Zone
        </h3>
        <button
          onClick={handleLogoutAll}
          className="px-4 py-2.5 rounded-xl text-sm font-medium
                     border border-red-300 dark:border-red-800 text-red-600 dark:text-red-400
                     hover:bg-red-50 dark:hover:bg-red-900/20
                     transition-all"
        >
          Log out all devices
        </button>
      </div>
    </div>
  );
}

// --- Sessions Tab ---
function SessionsTab() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const { sessions } = await api.getSessions();
      setSessions(sessions);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRevokeSession(sessionId: string) {
    try {
      await api.revokeSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
    } catch (err) {
      console.error("Failed to revoke session:", err);
    }
  }

  if (loading) {
    return <LoadingSpinner size="sm" />;
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-[#1a1a1a] dark:text-[#ececec] mb-2">
        Active Sessions
      </h2>
      <p className="text-sm text-[#a3a3a3] dark:text-[#a0a0a0] mb-6">
        Manage your active login sessions across devices
      </p>

      <div className="space-y-3">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`flex items-center justify-between p-4 rounded-xl border ${
              session.is_current
                ? "border-orange-200 dark:border-orange-800 bg-orange-50 dark:bg-orange-900/10"
                : "border-[#e8e8e8] dark:border-[#3a3a3a]"
            }`}
          >
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-[#1a1a1a] dark:text-[#ececec] text-sm">
                  {session.device_info || "Unknown device"}
                </span>
                {session.is_current && (
                  <span className="px-2 py-0.5 rounded text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-[#0f766e] dark:text-[#2dd4bf]">
                    Current
                  </span>
                )}
              </div>
              <p className="text-xs text-[#a3a3a3] dark:text-[#a0a0a0] mt-1">
                Created {new Date(session.created_at).toLocaleDateString()}
              </p>
            </div>
            {!session.is_current && (
              <button
                onClick={() => handleRevokeSession(session.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                Revoke
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// --- Danger Tab ---
function DangerTab() {
  const { logout } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDeleteAccount(e: FormEvent) {
    e.preventDefault();

    if (confirmText !== "DELETE") {
      setError("Please type DELETE to confirm");
      return;
    }

    if (!password) {
      setError("Please enter your password");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.deleteAccount(password);
      logout();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete account");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">
        Danger Zone
      </h2>
      <p className="text-sm text-[#a3a3a3] dark:text-[#a0a0a0] mb-6">
        Irreversible actions that permanently affect your account
      </p>

      {/* Warning Card */}
      <div className="p-6 rounded-xl border-2 border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-900/10">
        <div className="flex items-start gap-4">
          <div className="p-2 rounded-lg bg-red-100 dark:bg-red-900/30">
            <svg
              className="w-6 h-6 text-red-600 dark:text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-red-700 dark:text-red-300 mb-1">
              Delete Account
            </h3>
            <p className="text-sm text-red-600/80 dark:text-red-400/80 mb-4">
              Permanently delete your account and all associated data including:
            </p>
            <ul className="text-sm text-red-600/80 dark:text-red-400/80 space-y-1 mb-4">
              <li>• All your projects</li>
              <li>• All your chats and messages</li>
              <li>• All uploaded documents</li>
              <li>• Your profile and settings</li>
            </ul>
            <p className="text-sm font-medium text-red-700 dark:text-red-300">
              This action cannot be undone.
            </p>
          </div>
        </div>

        {!showConfirm ? (
          <button
            onClick={() => setShowConfirm(true)}
            className="mt-6 px-4 py-2 rounded-lg border-2 border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 font-medium hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
          >
            I want to delete my account
          </button>
        ) : (
          <form onSubmit={handleDeleteAccount} className="mt-6 space-y-4">
            <div className="p-4 rounded-lg bg-red-100 dark:bg-red-900/30">
              <label className="block text-sm font-medium text-red-700 dark:text-red-300 mb-2">
                Type "DELETE" to confirm
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE"
                className="w-full px-3 py-2 rounded-lg border border-red-300 dark:border-red-700 bg-white dark:bg-[#1a1a1a] text-[#1a1a1a] dark:text-[#ececec] placeholder-red-300 dark:placeholder-red-700"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-red-700 dark:text-red-300 mb-2">
                Enter your password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                className="w-full px-3 py-2 rounded-lg border border-red-300 dark:border-red-700 bg-white dark:bg-[#1a1a1a] text-[#1a1a1a] dark:text-[#ececec]"
              />
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-200 dark:bg-red-900/50 text-red-700 dark:text-red-300 text-sm">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setShowConfirm(false);
                  setPassword("");
                  setConfirmText("");
                  setError(null);
                }}
                className="flex-1 px-4 py-2 rounded-lg border border-[#e8e8e8] dark:border-[#3a3a3a] text-[#1a1a1a] dark:text-[#ececec] font-medium hover:bg-neutral-100 dark:hover:bg-[#2a2a2a] transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || confirmText !== "DELETE" || !password}
                className="flex-1 px-4 py-2 rounded-lg bg-red-600 text-white font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Deleting..." : "Delete My Account"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
