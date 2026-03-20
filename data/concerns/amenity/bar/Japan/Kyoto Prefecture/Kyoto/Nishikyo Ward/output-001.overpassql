[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Nishikyo Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
