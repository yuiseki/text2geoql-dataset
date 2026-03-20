[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Urawa Ward"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
