/**
 * Custom hooks for document upload and management.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "../api";
import type { ScopeType } from "../types";
import { chatKeys } from "./useChats";

export const documentKeys = {
  all: ["documents"] as const,
  byScope: (scopeType: ScopeType, scopeId: string) =>
    ["documents", scopeType, scopeId] as const,
};

export function useDocuments(scopeType: ScopeType, scopeId: string | null) {
  return useQuery({
    queryKey: scopeId
      ? documentKeys.byScope(scopeType, scopeId)
      : ["documents", "none"],
    queryFn: () =>
      scopeId ? api.listDocuments(scopeType, scopeId) : Promise.resolve([]),
    enabled: !!scopeId,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      scopeType,
      scopeId,
      file,
    }: {
      scopeType: ScopeType;
      scopeId: string;
      file: File;
    }) => {
      // Upload document — ingestion is triggered server-side automatically
      const result = await api.uploadDocument(scopeType, scopeId, file);
      return result;
    },
    onSuccess: (_, { scopeType, scopeId }) => {
      // Invalidate documents for this scope
      if (scopeType === "chat") {
        queryClient.invalidateQueries({
          queryKey: chatKeys.documents(scopeId),
        });
      }
      queryClient.invalidateQueries({
        queryKey: documentKeys.byScope(scopeType, scopeId),
      });
      // Invalidate limits to refresh UI immediately
      queryClient.invalidateQueries({
        queryKey: ["upload-limits", scopeType, scopeId],
      });
    },
  });
}
