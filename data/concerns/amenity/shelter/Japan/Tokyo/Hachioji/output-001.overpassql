[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Hachioji"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
