import React, { useState } from 'react';
import { StyleSheet, View, Alert, SafeAreaView, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { TextInput, Button, Text, Provider as PaperProvider, DefaultTheme, Card } from 'react-native-paper';

const theme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, primary: '#1A5276', accent: '#f1c40f' },
};

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  // États pour le formulaire
  const [isMachineValidated, setIsMachineValidated] = useState(false);
  const [machineNum, setMachineNum] = useState('');
  const [probleme, setProbleme] = useState('');
  const [action, setAction] = useState('');
  const [temps, setTemps] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://gmao-rhone-backend.onrender.com/login_gmao', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const result = await response.json();
      
      if (response.ok && result.status === "success") {
        setUser(result);
        setIsLoggedIn(true); // C'EST CETTE LIGNE QUI FAIT CHANGER LA PAGE
      } else {
        Alert.alert("Erreur", "Identifiants incorrects");
      }
    } catch (error) {
      Alert.alert("Erreur", "Serveur injoignable. Vérifie Render.");
    } finally {
      setLoading(false);
    }
  };

  // --- ÉCRAN 3 : FORMULAIRE FINAL ---
  if (isLoggedIn && isMachineValidated) {
    return (
      <PaperProvider theme={theme}>
        <SafeAreaView style={styles.container}>
          <ScrollView contentContainerStyle={styles.content}>
            <Text style={styles.title}>INTERVENTION</Text>
            <Text style={styles.subtitle}>Machine N° {machineNum}</Text>
            <Card style={styles.card}>
              <Card.Content>
                <TextInput label="Problème" value={probleme} onChangeText={setProbleme} mode="outlined" multiline style={styles.input} />
                <TextInput label="Action" value={action} onChangeText={setAction} mode="outlined" multiline style={styles.input} />
                <TextInput label="Temps (min)" value={temps} onChangeText={setTemps} mode="outlined" keyboardType="numeric" style={styles.input} />
                <Button mode="contained" onPress={() => Alert.alert("OK", "Données prêtes")} style={styles.button}>Envoyer</Button>
              </Card.Content>
            </Card>
            <Button onPress={() => setIsMachineValidated(false)}>Retour</Button>
          </ScrollView>
        </SafeAreaView>
      </PaperProvider>
    );
  }

  // --- ÉCRAN 2 : NUMÉRO DE MACHINE ---
  if (isLoggedIn) {
    return (
      <PaperProvider theme={theme}>
        <SafeAreaView style={styles.container}>
          <View style={styles.content}>
            <Text style={styles.title}>BIENVENUE</Text>
            <Text style={styles.subtitle}>{user?.nom}</Text>
            <TextInput label="N° MACHINE" value={machineNum} onChangeText={setMachineNum} mode="outlined" keyboardType="numeric" style={styles.inputLarge} />
            <Button mode="contained" onPress={() => setIsMachineValidated(true)} style={styles.button}>Valider Machine</Button>
            <Button onPress={() => setIsLoggedIn(false)} style={{marginTop: 20}}>Déconnexion</Button>
          </View>
        </SafeAreaView>
      </PaperProvider>
    );
  }

  // --- ÉCRAN 1 : CONNEXION ---
  return (
    <PaperProvider theme={theme}>
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>GMAO PRO</Text>
          <TextInput label="Utilisateur" value={username} onChangeText={setUsername} mode="outlined" style={styles.input} autoCapitalize="none" />
          <TextInput label="Mot de passe" value={password} onChangeText={setPassword} mode="outlined" secureTextEntry style={styles.input} />
          <Button mode="contained" onPress={handleLogin} loading={loading} style={styles.button}>Se connecter</Button>
        </View>
      </SafeAreaView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F4F6F7' },
  content: { padding: 20, flexGrow: 1, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1A5276' },
  subtitle: { fontSize: 18, textAlign: 'center', marginBottom: 20 },
  input: { marginBottom: 15 },
  inputLarge: { marginBottom: 20, fontSize: 24, textAlign: 'center' },
  button: { paddingVertical: 5 },
  card: { padding: 10, backgroundColor: 'white' }
});
