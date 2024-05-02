[out:json][timeout:30000];
area["name"="México"]->.outer;
area["name"="Guerrero"]->.inner;
(
  relation["boundary"="administrative"]["name"="Acapulco de Juárez"](area.inner)(area.outer);
);
out geom;
