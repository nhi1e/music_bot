import React, { useState, useEffect, useRef } from "react";
import { Header } from "@/components/Header";
import { LoginScreen } from "@/components/LoginScreen";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ChatContainer } from "@/components/ChatContainer";
import { ChatInput } from "@/components/ChatInput";
import { SpotifyUser, ChatMessage } from "@/types";
import { extractSpotifyImages } from "@/utils/spotifyImageExtractor";
import { extractSpotifyWrappedData } from "@/utils/spotifyWrappedExtractor";
import { forceScrollToBottom, smoothScrollToBottom } from "@/utils/scrollUtils";
import {
	checkAuthStatus,
	logout,
	sendChatMessage,
	getSpotifyLoginUrl,
} from "@/services/api";
import SpotifyWrapped from "@/components/SpotifyWrapped"; // Import SpotifyWrapped component
function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [isLoading, setIsLoading] = useState(true);
	const [user, setUser] = useState<SpotifyUser | null>(null);
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);
	const chatContainerRef = useRef<HTMLDivElement>(null);

	// Auto-scroll to the latest message
	useEffect(() => {
		const scrollToBottom = () => {
			smoothScrollToBottom(chatContainerRef);
		};

		// Multiple scroll attempts with increasing delays
		const timeouts = [
			setTimeout(scrollToBottom, 50),
			setTimeout(scrollToBottom, 150),
			setTimeout(scrollToBottom, 300),
			setTimeout(() => forceScrollToBottom(chatContainerRef), 500),
			setTimeout(() => forceScrollToBottom(chatContainerRef), 800),
		];

		return () => timeouts.forEach(clearTimeout);
	}, [messages, isTyping]);

	useEffect(() => {
		const checkAuth = async () => {
			// Check for auth callback parameters in URL
			const urlParams = new URLSearchParams(window.location.search);
			const authStatus = urlParams.get("auth");
			const username = urlParams.get("user");
			const errorMessage = urlParams.get("message");

			if (authStatus === "success") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				setIsAuthenticated(true);
				setIsLoading(false);
				return;
			}

			if (authStatus === "error") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert(
					`Authentication failed: ${decodeURIComponent(errorMessage || "Unknown error")}`
				);
				setIsLoading(false);
				return;
			}

			if (authStatus === "denied") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert("You denied access to Spotify. Please try again.");
				setIsLoading(false);
				return;
			}

			// Check if user is already authenticated via API
			try {
				const data = await checkAuthStatus();
				setIsAuthenticated(data.authenticated);
				if (data.authenticated && data.user) {
					setUser(data.user);
				}
			} catch (error) {
				console.error("Error checking auth status:", error);
				setIsAuthenticated(false);
			}

			setIsLoading(false);
		};

		checkAuth();
	}, []);

	const handleSpotifyLogin = () => {
		window.location.href = getSpotifyLoginUrl();
	};

	const handleLogout = async () => {
		try {
			await logout();
			setIsAuthenticated(false);
			setUser(null);
			setMessages([]);
		} catch (error) {
			console.error("Error logging out:", error);
		}
	};

	const handleSendMessage = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!inputValue.trim()) return;

		const userMessage: ChatMessage = {
			id: Date.now().toString(),
			content: inputValue,
			role: "user",
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsTyping(true);

		// Scroll to bottom after adding user message
		setTimeout(() => {
			smoothScrollToBottom(chatContainerRef);
		}, 50);

		try {
			const data = await sendChatMessage(inputValue);
			const responseContent =
				data.response || "Sorry, I couldn't process your request.";
			const { images: spotifyImages, cleanedText } =
				extractSpotifyImages(responseContent);
			const spotifyWrapped = extractSpotifyWrappedData(responseContent);

			console.log("Response from backend:", responseContent);
			console.log("Extracted Spotify images:", spotifyImages);
			console.log("Extracted Spotify Wrapped:", spotifyWrapped);
			console.log("Cleaned text:", cleanedText);

			// Clean the text again if we found wrapped data (remove the JSON)
			let finalCleanedText = cleanedText;
			if (spotifyWrapped) {
				finalCleanedText = cleanedText
					.replace(/SPOTIFY_WRAPPED_DATA:\{[\s\S]*?\}/, "")
					.trim();
			}

			const aiMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content: finalCleanedText,
				role: "assistant",
				timestamp: new Date(),
				spotifyImages: spotifyImages.length > 0 ? spotifyImages : undefined,
				spotifyWrapped: spotifyWrapped || undefined,
			};

			console.log("AI message with images:", aiMessage);
			setMessages((prev) => [...prev, aiMessage]);

			// Scroll to bottom after adding AI message
			setTimeout(() => {
				smoothScrollToBottom(chatContainerRef);
			}, 50);
		} catch (error) {
			console.error("Error sending message:", error);
			const errorMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content:
					"Sorry, there was an error processing your request. Please try again.",
				role: "assistant",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);

			setTimeout(() => {
				smoothScrollToBottom(chatContainerRef);
			}, 50);
		} finally {
			setIsTyping(false);
		}
	};

	if (isLoading) {
		return <LoadingSpinner />;
	}

	if (!isAuthenticated) {
		return <LoginScreen onSpotifyLogin={handleSpotifyLogin} />;
	}

	return (
		<div className="min-h-screen bg-black text-white flex flex-col font-mono">
			<Header user={user} onLogout={handleLogout} />
			<ChatContainer
				ref={chatContainerRef}
				messages={messages}
				isTyping={isTyping}
			/>
			<ChatInput
				value={inputValue}
				onChange={setInputValue}
				onSubmit={handleSendMessage}
				disabled={isTyping}
			/>
		</div>
	);
}

export default App;
