export interface SpotifyUser {
	id: string;
	display_name: string;
	email?: string;
	followers: number;
	images?: Array<{ url: string; height: number; width: number }>;
}

export interface SpotifyImage {
	url: string;
	title?: string;
	subtitle?: string;
	type?: "album" | "artist" | "playlist" | "track";
}

export interface ChatMessage {
	id: string;
	content: string;
	role: "user" | "assistant";
	timestamp: Date;
	spotifyImages?: SpotifyImage[];
}
