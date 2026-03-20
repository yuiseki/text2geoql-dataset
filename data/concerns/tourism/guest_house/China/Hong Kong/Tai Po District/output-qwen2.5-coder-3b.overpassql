[out:json][timeout:30];
area["name:en"="Tai Po District"][boundary=administrative]->.outer;
area["name:en"="Tai Po District"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
