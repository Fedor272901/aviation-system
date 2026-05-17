import { useAuthStore } from '../store/authStore';
import { isAdmin, isStaff } from '../utils/roles';
import { HomeGuest, HomeUser, HomeAdmin, HomeStaff } from '../components/home';

export function Home() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated || !user) {
    return <HomeGuest />;
  }

  if (isAdmin(user)) {
    return <HomeAdmin />;
  }

  if (isStaff(user)) {
    return <HomeStaff />;
  }

  return <HomeUser />;
}