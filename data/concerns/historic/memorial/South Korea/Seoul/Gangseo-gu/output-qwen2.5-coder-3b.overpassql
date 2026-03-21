[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangseo-gu"]->.inner;
(
  nwr["historic"="memorial"](area.inner)(area.outer);
);
out geom;
