import type { AuthUser } from '../types';

export function hasRole(user: AuthUser | null, role: string): boolean {
  if (!user) return false;
  return user.roles.includes(role);
}

export function isAdmin(user: AuthUser | null): boolean {
  return hasRole(user, 'admin');
}

export function isStaff(user: AuthUser | null): boolean {
  return hasRole(user, 'staff') || hasRole(user, 'crew');
}

export function isGuest(user: AuthUser | null, isAuthenticated: boolean): boolean {
  return !isAuthenticated || !user;
}