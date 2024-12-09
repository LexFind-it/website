import it.cnr.igsg.linkoln.Linkoln;
import it.cnr.igsg.linkoln.LinkolnDocument;
import it.cnr.igsg.linkoln.reference.LinkolnReference;

public class MainWrapper {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java MainWrapper <inputText>");
            return;
        }

        String text = args[0];

        try {
            LinkolnDocument linkolnDocument = Linkoln.run(text);

            if (!linkolnDocument.hasFailed()) {
                System.out.println("\n1) List of identified legal references:");

                for (LinkolnReference reference : linkolnDocument.getReferences()) {
                    System.out.println("\n\t- " + reference.getType() + " found: \"" + reference.getCitation() + "\"");

                    reference.getLinkolnIdentifiers().forEach(identifier -> {
                        System.out.println("\t\t " + identifier.getType() + " (" + identifier.getCode() + ") URL: " + identifier.getUrl());
                    });
                }

                System.out.println("\n\n2) HTML:\n\n" + linkolnDocument.getRendering("html"));
            } else {
                System.out.println("Failed to process the document.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
