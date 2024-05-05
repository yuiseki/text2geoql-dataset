[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Minato Ward"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
