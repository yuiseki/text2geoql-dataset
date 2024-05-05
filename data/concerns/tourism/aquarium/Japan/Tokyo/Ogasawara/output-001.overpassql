[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Ogasawara"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
