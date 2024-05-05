[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
