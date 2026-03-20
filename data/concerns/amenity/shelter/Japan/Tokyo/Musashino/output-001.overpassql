[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Musashino"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
