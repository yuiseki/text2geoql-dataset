[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Nishikan Ward"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
