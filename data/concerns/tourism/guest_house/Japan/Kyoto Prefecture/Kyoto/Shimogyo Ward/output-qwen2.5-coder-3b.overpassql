[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Shimogyo Ward"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
