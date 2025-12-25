import React, { useState } from 'react';
import { StyleSheet, View, Alert, SafeAreaView } from 'react-native';
import { TextInput, Button, Text, Provider as PaperProvider, DefaultTheme } from 'react-native-paper';

const theme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, primary: '#1A5276', accent: '#f1c40f' },
};

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert("Champs vides", "Merci de saisir ton identifiant et ton mot de passe.");
      return;
    }

    setLoading(true);
    try {
      // Connexion à ton serveur Render
      const response = await fetch('https://gmao-rhone-backend.onrender.com/login_gmao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, password: password }),
      });

      const result = await response.json();

      if (response.ok && result.status === "success") {
        Alert.alert("Connexion réussie", `Bonjour ${result.nom} !\nTu es connecté en tant que : ${result.role}`);
        // Plus tard, on naviguera vers l'écran de saisie ici
      } else {
        Alert.alert("Erreur", result.message || "Identifiants incorrects");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("Erreur Serveur", "Impossible de joindre le serveur. Vérifie que Render est bien 'Live'.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PaperProvider theme={theme}>
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>GMAO PRO</Text>
          <Text style={styles.subtitle}>Mademoiselle Rhône</Text>

          <TextInput
            label="Identifiant"
            value={username}
            onChangeText={setUsername}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            left={<TextInput.Icon icon="account" />}
          />

          <TextInput
            label="Mot de passe"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
            left={<TextInput.Icon icon="lock" />}
          />

          <Button 
            mode="contained" 
            onPress={handleLogin} 
            style={styles.button}
            loading={loading}
            disabled={loading}
            contentStyle={{ height: 50 }}
          >
            Se connecter
          </Button>

          <Text style={styles.version}>v1.0.2 - Serveur Connecté</Text>
        </View>
      </SafeAreaView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F4F6F7' },
  content: { flex: 1, padding: 25, justifyContent: 'center' },
  title: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', color: '#1A5276' },
  subtitle: { fontSize: 18, textAlign: 'center', marginBottom: 40, color: '#7F8C8D' },
  input: { marginBottom: 15, backgroundColor: '#fff' },
  button: { marginTop: 10, borderRadius: 8 },
  version: { textAlign: 'center', marginTop: 40, color: '#BDC3C7', fontSize: 10 }
});
