[out:json][timeout:30];
area["name:en"="Masovian Voivodeship"]->.outer;
area["name:en"="Warsaw"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;