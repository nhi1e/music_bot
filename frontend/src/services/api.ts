import { SpotifyUser } from "@/types";

const API_BASE_URL = "http://localhost:8080";

export const checkAuthStatus = async (): Promise<{
	authenticated: boolean;
	user?: SpotifyUser;
}> => {
	const response = await fetch(`${API_BASE_URL}/auth/status`);
	return await response.json();
};

export const logout = async (): Promise<void> => {
	await fetch(`${API_BASE_URL}/auth/logout`, { method: "POST" });
};

export const sendChatMessage = async (
	message: string
): Promise<{ response: string }> => {
	const response = await fetch(`${API_BASE_URL}/chat`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ message }),
	});

	if (!response.ok) {
		throw new Error(`HTTP error! status: ${response.status}`);
	}

	return await response.json();
};

export const getSpotifyLoginUrl = (): string => {
	return `${API_BASE_URL}/auth/spotify`;
};
