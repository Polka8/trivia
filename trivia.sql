-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Creato il: Mar 20, 2025 alle 09:22
-- Versione del server: 5.7.24
-- Versione PHP: 8.3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `trivia`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `domande`
--

CREATE TABLE `domande` (
  `ID_domanda` int(7) NOT NULL,
  `descrizione` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `punteggio`
--

CREATE TABLE `punteggio` (
  `ID_punteggio` int(7) NOT NULL,
  `valore` int(11) NOT NULL,
  `data_creazione` datetime NOT NULL,
  `email` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `risposte`
--

CREATE TABLE `risposte` (
  `ID_risposta` int(7) NOT NULL,
  `descrizione` varchar(500) NOT NULL,
  `stato` enum('corretta','sbagliata') NOT NULL,
  `id_domanda` int(7) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Struttura della tabella `utente`
--

CREATE TABLE `utente` (
  `email` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL,
  `nome` varchar(50) NOT NULL,
  `cognome` varchar(50) NOT NULL,
  `ruolo` enum('admin','cliente') NOT NULL,
  `creato_il` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `domande`
--
ALTER TABLE `domande`
  ADD PRIMARY KEY (`ID_domanda`);

--
-- Indici per le tabelle `punteggio`
--
ALTER TABLE `punteggio`
  ADD PRIMARY KEY (`ID_punteggio`),
  ADD KEY `utente_punteggio` (`email`);

--
-- Indici per le tabelle `risposte`
--
ALTER TABLE `risposte`
  ADD PRIMARY KEY (`ID_risposta`),
  ADD KEY `domande_risposte` (`id_domanda`);

--
-- Indici per le tabelle `utente`
--
ALTER TABLE `utente`
  ADD PRIMARY KEY (`email`);

--
-- Limiti per le tabelle scaricate
--

--
-- Limiti per la tabella `punteggio`
--
ALTER TABLE `punteggio`
  ADD CONSTRAINT `utente_punteggio` FOREIGN KEY (`email`) REFERENCES `utente` (`email`);

--
-- Limiti per la tabella `risposte`
--
ALTER TABLE `risposte`
  ADD CONSTRAINT `domande_risposte` FOREIGN KEY (`id_domanda`) REFERENCES `domande` (`ID_domanda`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
