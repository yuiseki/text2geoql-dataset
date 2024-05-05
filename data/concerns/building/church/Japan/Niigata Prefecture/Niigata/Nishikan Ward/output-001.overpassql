[out:json][timeout:30000];
area["name:en"="Niigata"]->.outer;
area["name:en"="Nishikan Ward"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
