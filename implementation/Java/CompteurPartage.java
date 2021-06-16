class Compteur {
    private int compteur = 0;
    public void inc() {
        compteur++;
        System.out.println("inc -> " + this.compteur);
    }
}


class Fils implements Runnable {
    private Compteur c;
    Fils(Compteur c) {
        this.c = c;
    }
    public void run() {
        for (int i = 1; i <= 10; i++) {
            c.inc();

            // Sleep pour donner la main à l'autre thread
            try {
                Thread.sleep(100);
            } catch (InterruptedException ie) {
                System.err.println("Sleep impossible");
            }

        }
    }
}


public class CompteurPartage {
    public static void main(String[] args) {

        // création du compteur c
        Compteur c = new Compteur();

        // création et lancement du fil1 (incrémente 10x cpt de 1)
        Fils fil1 = new Fils (c);
        Thread client1 = new Thread(fil1);
        client1.start();

        // création et lancement du fil2 (incrémente 10x cpt de 1)
        Fils fil2 = new Fils (c);
        Thread client2 = new Thread(fil2);
        client2.start();

    }
}