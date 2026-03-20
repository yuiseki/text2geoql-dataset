[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Sakura Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
