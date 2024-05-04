[out:json][timeout:30000];
area["name:en"="Kobe"]->.outer;
area["name:en"="Chuo"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
