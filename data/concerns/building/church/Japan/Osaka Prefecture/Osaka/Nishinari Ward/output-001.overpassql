[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Nishinari Ward"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
