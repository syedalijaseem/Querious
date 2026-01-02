/**
 * Custom hooks for Projects using TanStack Query.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "../api";
import type { Project } from "../types";

export const projectKeys = {
  all: ["projects"] as const,
  detail: (id: string) => ["projects", id] as const,
};

export function useProjects() {
  return useQuery({
    queryKey: projectKeys.all,
    queryFn: api.listProjects,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: () => api.getProject(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (name: string) => api.createProject(name),
    onSuccess: (newProject) => {
      queryClient.setQueryData<Project[]>(projectKeys.all, (old) =>
        old ? [newProject, ...old] : [newProject]
      );
      // Invalidate project count for limits
      queryClient.invalidateQueries({ queryKey: ["projects-count"] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.deleteProject(id),
    // Optimistic update - remove immediately from UI
    onMutate: async (id) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: projectKeys.all });

      // Snapshot previous value
      const previousProjects = queryClient.getQueryData<Project[]>(
        projectKeys.all
      );

      // Optimistically remove from list
      queryClient.setQueryData<Project[]>(projectKeys.all, (old) =>
        old?.filter((p) => p.id !== id)
      );

      return { previousProjects };
    },
    onError: (_err, _id, context) => {
      // Rollback on error
      if (context?.previousProjects) {
        queryClient.setQueryData(projectKeys.all, context.previousProjects);
      }
    },
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: projectKeys.detail(id) });
    },
    onSettled: () => {
      // Refetch to ensure consistency
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      // Invalidate project count for limits
      queryClient.invalidateQueries({ queryKey: ["projects-count"] });
    },
  });
}
