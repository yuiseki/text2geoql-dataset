[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Nishikyo Ward"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
