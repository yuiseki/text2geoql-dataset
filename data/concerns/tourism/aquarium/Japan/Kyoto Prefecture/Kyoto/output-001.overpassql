[out:json][timeout:30000];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
