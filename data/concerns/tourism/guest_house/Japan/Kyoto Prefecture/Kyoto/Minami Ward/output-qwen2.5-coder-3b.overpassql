[out:json][timeout:30];
area["name:en"="Minami Ward"][boundary=administrative]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
