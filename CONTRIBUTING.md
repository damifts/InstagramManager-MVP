# Contributing

Guida minima per contribuire al progetto.

## Flusso rapido

1. Parti sempre da main aggiornato.
2. Crea un branch dedicato.
3. Fai commit piccoli e leggibili.
4. Apri una Pull Request.
5. Fai merge solo dopo review.

## Branch naming

- feat/... nuove funzionalita
- fix/... bug fix
- docs/... documentazione
- refactor/... semplificazioni interne

Esempio:

```cmd
git checkout main
git pull
git checkout -b feat/migliora-client
```

## Commit naming

Formato consigliato:

- feat: ...
- fix: ...
- docs: ...
- refactor: ...

Esempio:

```cmd
git add .
git commit -m "feat: semplifica sidebar client"
```

## Pull Request

Checklist consigliata:

- descrizione breve di cosa cambia
- come testare la modifica
- eventuali limiti noti
- screenshot solo se cambia la UI

## Regola pratica

Se la modifica e grande, spezzala in piu PR piccole.
