[out:json][timeout:30];
area["name:en"="Nanshan District"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
