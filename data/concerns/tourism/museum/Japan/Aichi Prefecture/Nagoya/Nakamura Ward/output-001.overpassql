[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Nakamura Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
