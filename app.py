import React, { useState } from 'react';
import { StyleSheet, View, Alert, SafeAreaView, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
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
  
  // États pour le formulaire d'intervention
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
        setIsLoggedIn(true);
      } else {
        Alert.alert("Erreur", "Identifiants incorrects");
      }
    } catch (error) {
      Alert.alert("Erreur", "Serveur injoignable");
    } finally {
      setLoading(false);
    }
  };

  const envoyerIntervention = async () => {
    if (!probleme || !action || !temps) {
      Alert.alert("Champs vides", "Merci de remplir toutes les rubriques.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('https://gmao-rhone-backend.onrender.com/save_compteurs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          machine_num: machineNum,
          probleme: probleme,
          action_realisee: action,
          temps: temps,
          operateur: user.nom
        }),
      });
      const result = await response.json();
      if (response.ok) {
        Alert.alert("Envoyé !", "L'intervention a été enregistrée.");
        // Reset du formulaire
        setProbleme('');
        setAction('');
        setTemps('');
        setIsMachineValidated(false);
      }
    } catch (error) {
      Alert.alert("Erreur", "Impossible d'envoyer les données.");
    } finally {
      setLoading(false);
    }
  };

  // ÉCRAN 3 : FORMULAIRE D'INTERVENTION
  if (isLoggedIn && isMachineValidated) {
    return (
      <PaperProvider theme={theme}>
        <SafeAreaView style={styles.container}>
          <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{flex: 1}}>
            <ScrollView contentContainerStyle={styles.content}>
              <Text style={styles.title}>INTERVENTION</Text>
              <Text style={styles.subtitle}>Machine N° {machineNum}</Text>
              
              <Card style={styles.card}>
                <Card.Content>
                  <TextInput label="Problème constaté" value={probleme} onChangeText={setProbleme} mode="outlined" multiline numberOfLines={3} style={styles.input} />
                  <TextInput label="Action réalisée" value={action} onChangeText={setAction} mode="outlined" multiline numberOfLines={3} style={styles.input} />
                  <TextInput label="Temps passé (en min)" value={temps} onChangeText={setTemps} mode="outlined" keyboardType="numeric" style={styles.input} />
                  
                  <Button mode="contained" onPress={envoyerIntervention} loading={loading} style={styles.button}>
                    Enregistrer l'action
                  </Button>
                </Card.Content>
              </Card>

              <Button mode="text" onPress={() => setIsMachineValidated(false)} style={{marginTop: 10}}>
                Changer de machine
              </Button>
            </ScrollView>
          </KeyboardAvoidingView>
        </SafeAreaView>
      </PaperProvider>
    );
  }

  // ÉCRAN 2 : SÉLECTION MACHINE
  if (isLoggedIn) {
    return (
      <PaperProvider theme={theme}>
        <SafeAreaView style={styles.container}>
          <View style={styles.content}>
            <Text style={styles.title}>Machine</Text>
            <Text style={styles.subtitle}>Saisis le numéro de machine :</Text>
            <TextInput label="N°" value={machineNum} onChangeText={setMachineNum} mode="outlined" keyboardType="numeric" style={styles.inputLarge} />
            <Button mode="contained" onPress={() => machineNum ? setIsMachineValidated(true) : null} style={styles.button}>Valider</Button>
            <Button mode="text" onPress={() => setIsLoggedIn(false)} style={{marginTop: 30}}>Déconnexion</Button>
          </View>
        </SafeAreaView>
      </PaperProvider>
    );
  }

  // ÉCRAN 1 : CONNEXION
  return (
    <PaperProvider theme={theme}>
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>GMAO PRO</Text>
          <Text style={styles.subtitle}>Connectez-vous</Text>
          <TextInput label="Identifiant" value={username} onChangeText={setUsername} mode="outlined" style={styles.input} autoCapitalize="none" />
          <TextInput label="Mot de passe" value={password} onChangeText={setPassword} mode="outlined" secureTextEntry style={styles.input} />
          <Button mode="contained" onPress={handleLogin} loading={loading} style={styles.button}>Se connecter</Button>
        </View>
      </SafeAreaView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F4F6F7' },
  content: { padding: 25, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1A5276', marginTop: 20 },
  subtitle: { fontSize: 16, textAlign: 'center', marginBottom: 20, color: '#7F8C8D' },
  input: { marginBottom: 12, backgroundColor: 'white' },
  inputLarge: { marginBottom: 20, textAlign: 'center', fontSize: 24 },
  button: { marginTop: 10, paddingVertical: 5 },
  card: { elevation: 4, borderRadius: 10, backgroundColor: 'white' }
});
