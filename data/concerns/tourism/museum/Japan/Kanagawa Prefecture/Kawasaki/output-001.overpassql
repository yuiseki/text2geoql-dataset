[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Kawasaki"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;