[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Shimogyo Ward"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.auter);
);
out geom;
